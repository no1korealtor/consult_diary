import sys
import os
import re
import urllib.request
import urllib.parse
import json
from datetime import datetime

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle

# Import utilities from trade_viewer
from trade_viewer import (
    get_kakao_address_info,
    get_recent_transactions
)

# Mapping of administrative dongs and minor legal dongs to legal dongs for combined analysis
DONG_GROUPS = {
    "성산2동": {
        "dongs": ["성산동", "중동"],
        "display": "성산2동 (성산동, 중동)"
    },
    "중동": {
        "dongs": ["성산동", "중동"],
        "display": "성산2동 (성산동, 중동)"
    },
    "서강동": {
        "dongs": ["창전동", "상수동", "하중동", "신정동", "당인동"],
        "display": "서강동 (창전/상수/하중/신정/당인동)"
    },
    "신수동": {
        "dongs": ["신수동", "현석동", "구수동"],
        "display": "신수동 (신수/현석/구수동)"
    },
    "공덕동": {
        "dongs": ["공덕동", "신공덕동"],
        "display": "공덕동 (공덕/신공덕동)"
    },
    "신공덕동": {
        "dongs": ["공덕동", "신공덕동"],
        "display": "공덕동 (공덕/신공덕동)"
    },
    "도화동": {
        "dongs": ["도화동", "마포동"],
        "display": "도화동 (도화/마포동)"
    },
    "마포동": {
        "dongs": ["도화동", "마포동"],
        "display": "도화동 (도화/마포동)"
    },
    "대흥동": {
        "dongs": ["대흥동", "노고산동"],
        "display": "대흥동 (대흥/노고산동)"
    },
    "노고산동": {
        "dongs": ["대흥동", "노고산동"],
        "display": "대흥동 (대흥/노고산동)"
    },
    "서교동": {
        "dongs": ["서교동", "동교동"],
        "display": "서교동 (서교/동교동)"
    },
    "동교동": {
        "dongs": ["서교동", "동교동"],
        "display": "서교동 (서교/동교동)"
    }
}


def estimate_supply_pyung(exclu_area):
    """
    국토교통부 실거래가 전용면적(㎡)을 한국 아파트의 일반적인 공급평형(분양평형)으로 변환합니다.
    """
    if not exclu_area:
        return 0
    try:
        exclu_area = float(exclu_area)
    except ValueError:
        return 0
        
    pyung_excl = exclu_area * 0.3025
    if exclu_area < 40:
        ratio = 0.70  # 소형: 전용률 약 70%
    elif 40 <= exclu_area < 55:
        ratio = 0.72  # 20평형대 미만: 전용률 약 72%
    elif 55 <= exclu_area < 70:
        ratio = 0.73  # 24~26평형: 전용률 약 73% (59㎡ -> 약 25평)
    elif 70 <= exclu_area < 80:
        ratio = 0.75  # 29~31평형: 전용률 약 75%
    elif 80 <= exclu_area < 90:
        ratio = 0.78  # 32~35평형: 전용률 약 78% (84㎡ -> 약 32.8평)
    elif 90 <= exclu_area < 110:
        ratio = 0.79  # 36~40평형: 전용률 약 79%
    elif 110 <= exclu_area < 130:
        ratio = 0.81  # 40~45평형: 전용률 약 81% (117.9㎡ -> 약 44평)
    elif 130 <= exclu_area < 150:
        ratio = 0.83  # 48~52평형: 전용률 약 83% (136.5㎡ -> 약 50평)
    return int(round(pyung_excl / ratio))


def get_villa_group(area):
    """
    연립/다세대/빌라의 전용면적(㎡)을 방수로 추정하여 그룹 이름을 반환합니다.
    """
    if not area:
        return "원룸형 (전용 20㎡ 미만)"
    try:
        area = float(area)
    except:
        return "원룸형 (전용 20㎡ 미만)"
        
    if area < 20:
        return "원룸형 (전용 20㎡ 미만)"
    elif area < 40:
        return "투룸형 (전용 20~40㎡)"
    elif area < 60:
        return "쓰리룸형 (전용 40~60㎡)"
    else:
        return "대형 (전용 60㎡ 이상)"


def is_basement_transaction(t):
    """
    거래 데이터의 층수를 분석하여 지하층(반지하) 여부를 반환합니다.
    """
    flr_str = str(t.get('floor') or t.get('flrNo') or '').strip()
    if not flr_str:
        return False
    if '지하' in flr_str or 'b' in flr_str.lower():
        return True
    if flr_str.startswith('-'):
        return True
    try:
        if int(flr_str) < 0:
            return True
    except ValueError:
        pass
    return False


_admin_dong_cache = {}

def get_kakao_admin_dong(address_str):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": "KakaoAK 133155e52871811db4337080ae0a2d13"}
    params = urllib.parse.urlencode({"query": address_str})
    req = urllib.request.Request(f"{url}?{params}", headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            res_text = response.read().decode('utf-8')
            data = json.loads(res_text)
            if data.get("documents"):
                doc = data["documents"][0]
                addr = doc.get("address", {})
                if addr:
                    return addr.get("region_3depth_h_name", "")
    except Exception as e:
        pass
    return ""

_cache_loaded = False

def load_admin_dong_cache():
    global _admin_dong_cache, _cache_loaded
    if _cache_loaded:
        return
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cache_path = os.path.join(base_dir, "admin_dong_cache.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in data.items():
                    parts = k.split("|")
                    if len(parts) == 3:
                        _admin_dong_cache[tuple(parts)] = v
        except Exception as e:
            print(f"Error loading admin dong cache: {e}")
    _cache_loaded = True

def save_admin_dong_cache():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cache_path = os.path.join(base_dir, "admin_dong_cache.json")
    try:
        data = {}
        for k, v in _admin_dong_cache.items():
            data["|".join(k)] = v
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving admin dong cache: {e}")

def get_cached_admin_dong(full_region_name, bjdong, jibun):
    if not jibun:
        return ""
    load_admin_dong_cache()
    key = (full_region_name, bjdong, jibun)
    if key in _admin_dong_cache:
        return _admin_dong_cache[key]
        
    query_str = f"{full_region_name} {bjdong} {jibun}"
    h_dong = get_kakao_admin_dong(query_str)
    _admin_dong_cache[key] = h_dong
    save_admin_dong_cache()
    return h_dong

def normalize_h_dong_name(name):
    if not name:
        return ""
    name = name.strip()
    name = re.sub(r'제(\d+동)', r'\1', name)
    return name


def local_format_price(val):
    if val >= 10000:
        eok = int(val // 10000)
        man = int(val % 10000)
        return f"{eok}억 {man:,}만" if man > 0 else f"{eok}억"
    else:
        return f"{int(val):,}만"

def register_korean_font():
    font_paths = [
        "C:\\Windows\\Fonts\\malgun.ttf",       # Malgun Gothic
        "C:\\Windows\\Fonts\\gulim.ttc",        # Gulim
        "C:\\Windows\\Fonts\\batang.ttc",       # Batang
        "C:\\Windows\\Fonts\\맑은.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('KoreanFont', path))
                return 'KoreanFont'
            except:
                continue
    return 'Helvetica'

def load_member_info():
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    p_path = os.path.join(base, "member_info.json")
    if os.path.exists(p_path):
        try:
            with open(p_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            profile = data.get("profile", data)
            
            # Split profile name if it contains '|'
            if profile and isinstance(profile, dict) and "name" in profile:
                name_val = profile["name"]
                if "|" in name_val:
                    parts = name_val.split("|")
                    profile["name"] = parts[0].strip()
                    profile["office_name"] = parts[1].strip()
            
            office = profile.get("office_name") or profile.get("office")
            
            if not office:
                print("\n[안내] 현재 회원 정보에 중개사무소 명칭(상호)이 등록되어 있지 않습니다.")
                custom_office = input("보고서에 표시할 중개사무소 상호명을 입력해 주세요 (예: 한강공인중개사사무소): ").strip()
                if custom_office:
                    if isinstance(data, dict) and "profile" in data:
                        data["profile"]["office_name"] = custom_office
                    elif isinstance(data, dict):
                        data["office_name"] = custom_office
                    
                    try:
                        with open(p_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        print(f" -> 입력하신 상호명 '{custom_office}'이(가) 저장되었습니다. (추후 타 보고서에도 자동 반영)")
                        profile["office_name"] = custom_office
                    except Exception as e:
                        print(f" -> 저장 실패: {e}")
                        
            return profile
        except:
            pass
    return None

def calculate_market_conversion_rate(transactions):
    jeonses = [t for t in transactions if t.get('_trade_type') == '전세']
    wolses = [t for t in transactions if t.get('_trade_type') == '월세']
    
    if not jeonses or not wolses:
        return None
    
    jeonse_deposits = []
    for item in jeonses:
        deposit_str = str(item.get('rowPrice', '') or item.get('deposit', '') or item.get('guaranteeAmt', '')).strip().replace(',', '')
        if deposit_str:
            try:
                jeonse_deposits.append(float(deposit_str))
            except:
                pass
                
    wolse_deposits = []
    wolse_rents = []
    for item in wolses:
        deposit_str = str(item.get('rowPrice', '') or item.get('deposit', '') or item.get('guaranteeAmt', '')).strip().replace(',', '')
        rent_str = str(item.get('monthlyRent', '') or item.get('monthly', '')).strip().replace(',', '')
        if deposit_str and rent_str:
            try:
                dep = float(deposit_str)
                rent = float(rent_str)
                if rent > 0:
                    wolse_deposits.append(dep)
                    wolse_rents.append(rent)
            except:
                pass
                
    if not jeonse_deposits or not wolse_deposits or not wolse_rents:
        return None
        
    avg_jeonse = sum(jeonse_deposits) / len(jeonse_deposits)
    avg_wolse_dep = sum(wolse_deposits) / len(wolse_deposits)
    avg_wolse_rent = sum(wolse_rents) / len(wolse_rents)
    
    if avg_jeonse <= avg_wolse_dep:
        return None
        
    conversion_rate = (avg_wolse_rent * 12) / (avg_jeonse - avg_wolse_dep) * 100
    
    if 1.0 <= conversion_rate <= 20.0:
        return conversion_rate
        
    return None

def analyze_conversion_rate_segments(transactions, prop_type):
    jeonses = [t for t in transactions if t.get('_trade_type') == '전세']
    wolses = [t for t in transactions if t.get('_trade_type') == '월세']
    
    if not jeonses or not wolses:
        return {}
    
    def get_dep(item):
        val = str(item.get('rowPrice', '') or item.get('deposit', '') or item.get('guaranteeAmt', '')).strip().replace(',', '')
        return float(val) if val else 0.0

    def get_rent(item):
        val = str(item.get('monthlyRent', '') or item.get('monthly', '')).strip().replace(',', '')
        return float(val) if val else 0.0

    def get_area(item):
        val = item.get('excluUseAr') or item.get('totalFloorAr')
        return float(val) if val else 0.0

    size_groups = {}
    for j in jeonses:
        area = get_area(j)
        dep = get_dep(j)
        if area > 0 and dep > 0:
            size_key = round(area)
            size_groups.setdefault(size_key, []).append(dep)

    avg_jeonse_by_size = {k: sum(v)/len(v) for k, v in size_groups.items() if len(v) > 0}
    
    thresholds = [3000, 10000] if prop_type == '2' else [5000, 20000]
    
    rates_g1 = []
    rates_g2 = []
    rates_g3 = []
    
    for w in wolses:
        dep = get_dep(w)
        rent = get_rent(w)
        area = get_area(w)
        if dep <= 0 or rent <= 0 or area <= 0:
            continue
        
        closest_size = min(avg_jeonse_by_size.keys(), key=lambda x: abs(x - area)) if avg_jeonse_by_size else None
        if not closest_size or abs(closest_size - area) > 5:
            continue
            
        avg_j_dep = avg_jeonse_by_size[closest_size]
        if avg_j_dep <= dep:
            continue
            
        rate = (rent * 12) / (avg_j_dep - dep) * 100
        if 1.0 <= rate <= 25.0:
            if dep < thresholds[0]:
                rates_g1.append(rate)
            elif dep < thresholds[1]:
                rates_g2.append(rate)
            else:
                rates_g3.append(rate)
                
    return {
        'thresholds': thresholds,
        'g1_rate': sum(rates_g1)/len(rates_g1) if rates_g1 else None,
        'g1_count': len(rates_g1),
        'g2_rate': sum(rates_g2)/len(rates_g2) if rates_g2 else None,
        'g2_count': len(rates_g2),
        'g3_rate': sum(rates_g3)/len(rates_g3) if rates_g3 else None,
        'g3_count': len(rates_g3)
    }

def create_trend_chart_drawing(trend_data, apt_name, pyung_label="30평대"):
    prices = []
    jeonse_prices = []
    counts = []
    jeonse_counts = []
    
    for item in trend_data:
        if item.get('avg') is not None:
            prices.append(item['avg'])
        if item.get('jeonse_avg') is not None:
            jeonse_prices.append(item['jeonse_avg'])
        counts.append(item.get('count', 0))
        jeonse_counts.append(item.get('jeonse_count', 0))
        
    all_prices = prices + jeonse_prices
    if not all_prices:
        d = Drawing(515, 100)
        d.add(Rect(0, 0, 515, 100, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#E2E8F0')))
        d.add(String(257, 50, "최근 12개월간 매매 및 전세 거래 내역이 없습니다.", textAnchor='middle', fontName='KoreanFont', fontSize=10, fillColor=colors.HexColor('#718096')))
        return d

    min_p = min(all_prices)
    max_p = max(all_prices)
    if min_p == max_p:
        min_p = max(0, min_p - 10000)
        max_p = max_p + 10000
    else:
        diff = max_p - min_p
        min_p = max(0, min_p - diff * 0.2)
        max_p = max_p + diff * 0.2

    # Volume (count) Y-axis scale
    max_c = max(counts + jeonse_counts) if (counts + jeonse_counts) else 0
    if max_c < 4:
        max_c = 4
    
    dw = 515
    dh = 180
    d = Drawing(dw, dh)
    
    # Background card
    d.add(Rect(0, 0, dw, dh, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=1, rx=5, ry=5))
    
    # Title
    d.add(String(15, dh - 20, f"📈 {apt_name} {pyung_label} 거래 동향", fontName='KoreanFont', fontSize=8.5, fillColor=colors.HexColor('#0F172A'), textAnchor='start'))
    
    # Legends (dw = 515)
    # 매매 평균가
    d.add(Rect(dw - 230, dh - 22, 8, 6, fillColor=colors.HexColor('#1E293B'), strokeColor=colors.HexColor('#0F172A'), strokeWidth=0.5))
    d.add(String(dw - 218, dh - 23, "매매가", fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#475569')))
    
    # 전세 평균가
    d.add(Rect(dw - 180, dh - 22, 8, 6, fillColor=colors.HexColor('#64748B'), strokeColor=colors.HexColor('#475569'), strokeWidth=0.5))
    d.add(String(dw - 168, dh - 23, "전세가", fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#475569')))
    
    # 매매 건수
    d.add(Line(dw - 125, dh - 19, dw - 115, dh - 19, strokeColor=colors.HexColor('#B45309'), strokeWidth=1.5))
    d.add(Circle(dw - 120, dh - 19, 1.5, fillColor=colors.HexColor('#B45309'), strokeColor=None))
    d.add(String(dw - 110, dh - 23, "매매건수", fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#475569')))
    
    # 전세 건수
    d.add(Line(dw - 65, dh - 19, dw - 55, dh - 19, strokeColor=colors.HexColor('#0D9488'), strokeWidth=1.5))
    d.add(Circle(dw - 60, dh - 19, 1.5, fillColor=colors.HexColor('#0D9488'), strokeColor=None))
    d.add(String(dw - 50, dh - 23, "전세건수", fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#475569')))

    cx = 45
    cy = 30
    cw = dw - 85 
    ch = dh - 70
    
    # Left Y-axis Grid Lines & Labels (Price)
    for i in range(3):
        y_val = cy + i * (ch / 2)
        price_val = min_p + i * ((max_p - min_p) / 2)
        d.add(Line(cx, y_val, cx + cw, y_val, strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=0.5))
        if price_val >= 10000:
            lbl = f"{price_val/10000:.1f}억"
        else:
            lbl = f"{int(price_val):,}만"
        d.add(String(cx - 5, y_val - 3, lbl, fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#718096'), textAnchor='end'))
        
    # Right Y-axis Grid Labels (Count)
    for i in range(3):
        y_val = cy + i * (ch / 2)
        c_val = int(i * (max_c / 2))
        d.add(String(cx + cw + 5, y_val - 3, f"{c_val}건", fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#718096'), textAnchor='start'))

    num_bars = len(trend_data)
    bar_space = (cw / num_bars)
    bar_width = bar_space * 0.35
    
    # Draw bars (price) first
    for idx, item in enumerate(trend_data):
        x_center = cx + idx * bar_space + bar_space / 2
        month = item['month']
        avg_val = item.get('avg')
        jeonse_val = item.get('jeonse_avg')
        
        # X-axis label
        d.add(String(x_center, cy - 15, month, fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#4A5568'), textAnchor='middle'))
        
        # 1. 매매 막대 (왼쪽 배치)
        x_trade = x_center - bar_width - 1
        if avg_val is not None:
            h_trade = ((avg_val - min_p) / (max_p - min_p)) * ch
            h_trade = max(5, h_trade)
            d.add(Rect(x_trade, cy, bar_width, h_trade, fillColor=colors.HexColor('#1E293B'), strokeColor=colors.HexColor('#0F172A'), strokeWidth=0.5, rx=1, ry=1))
            
            # 매매 가격 텍스트 (막대 위)
            if avg_val >= 10000:
                eok = int(avg_val // 10000)
                man = int(avg_val % 10000)
                price_lbl = f"{eok}.{int(man/1000)}억" if man > 0 else f"{eok}억"
            else:
                price_lbl = f"{int(avg_val):,}만"
            d.add(String(x_trade + bar_width / 2, cy + h_trade + 3, price_lbl, fontName='KoreanFont', fontSize=6, fillColor=colors.HexColor('#1E293B'), textAnchor='middle'))
        else:
            d.add(String(x_trade + bar_width / 2, cy + 5, "-", fontName='KoreanFont', fontSize=6, fillColor=colors.HexColor('#CBD5E0'), textAnchor='middle'))
            
        # 2. 전세 막대 (오른쪽 배치)
        x_jeonse = x_center + 1
        if jeonse_val is not None:
            h_jeonse = ((jeonse_val - min_p) / (max_p - min_p)) * ch
            h_jeonse = max(5, h_jeonse)
            d.add(Rect(x_jeonse, cy, bar_width, h_jeonse, fillColor=colors.HexColor('#64748B'), strokeColor=colors.HexColor('#475569'), strokeWidth=0.5, rx=1, ry=1))
            
            # 전세 가격 텍스트 (막대 위)
            if jeonse_val >= 10000:
                eok = int(jeonse_val // 10000)
                man = int(jeonse_val % 10000)
                j_price_lbl = f"{eok}.{int(man/1000)}억" if man > 0 else f"{eok}억"
            else:
                j_price_lbl = f"{int(jeonse_val):,}만"
            d.add(String(x_jeonse + bar_width / 2, cy + h_jeonse + 3, j_price_lbl, fontName='KoreanFont', fontSize=6, fillColor=colors.HexColor('#475569'), textAnchor='middle'))
        else:
            d.add(String(x_jeonse + bar_width / 2, cy + 5, "-", fontName='KoreanFont', fontSize=6, fillColor=colors.HexColor('#CBD5E0'), textAnchor='middle'))

    # Draw lines (count) on top of bars
    points_trade = []
    points_jeonse = []
    
    for idx, item in enumerate(trend_data):
        x_center = cx + idx * bar_space + bar_space / 2
        count_trade = item.get('count', 0)
        count_jeonse = item.get('jeonse_count', 0)
        
        px = x_center
        py_trade = cy + (count_trade / max_c) * ch
        py_jeonse = cy + (count_jeonse / max_c) * ch
        
        points_trade.append((px, py_trade, count_trade))
        points_jeonse.append((px, py_jeonse, count_jeonse))
        
    # Draw connecting lines for trade
    for i in range(len(points_trade) - 1):
        x1, y1, _ = points_trade[i]
        x2, y2, _ = points_trade[i+1]
        d.add(Line(x1, y1, x2, y2, strokeColor=colors.HexColor('#B45309'), strokeWidth=1.2))
        
    # Draw connecting lines for jeonse
    for i in range(len(points_jeonse) - 1):
        x1, y1, _ = points_jeonse[i]
        x2, y2, _ = points_jeonse[i+1]
        d.add(Line(x1, y1, x2, y2, strokeColor=colors.HexColor('#0D9488'), strokeWidth=1.2))
        
    # Draw dots and count labels for trade
    for px, py, count in points_trade:
        if count > 0:
            d.add(Circle(px - 4, py, 2, fillColor=colors.HexColor('#B45309'), strokeColor=colors.white, strokeWidth=0.5))
            d.add(String(px - 4, py + 4, f"{count}", fontName='KoreanFont', fontSize=6, fillColor=colors.HexColor('#B45309'), textAnchor='middle'))
            
    # Draw dots and count labels for jeonse
    for px, py, count in points_jeonse:
        if count > 0:
            d.add(Circle(px + 4, py, 2, fillColor=colors.HexColor('#0D9488'), strokeColor=colors.white, strokeWidth=0.5))
            d.add(String(px + 4, py + 4, f"{count}", fontName='KoreanFont', fontSize=6, fillColor=colors.HexColor('#0D9488'), textAnchor='middle'))
            
    return d

def generate_market_report_pdf(pdf_filename, bjdong_nm, apt_txs, villa_txs, member_info=None, region_prefix="서울특별시 마포구", rep_apt_name=None, trend_data=None, filtered_apt_txs=None):
    font_name = register_korean_font()
    if filtered_apt_txs is None:
        filtered_apt_txs = apt_txs
        
    # Calculate 24-month period range dynamically
    now = datetime.now()
    end_year = now.year
    end_month = now.month
    start_month = end_month - 23
    start_year = end_year
    while start_month <= 0:
        start_month += 12
        start_year -= 1
    period_str = f"{start_year}.{str(start_month).zfill(2)} ~ {end_year}.{str(end_month).zfill(2)}"
    
    # Calculate 6-month period range dynamically
    start_month_6 = end_month - 5
    start_year_6 = end_year
    while start_month_6 <= 0:
        start_month_6 += 12
        start_year_6 -= 1
    period_str_6 = f"{start_year_6}.{str(start_month_6).zfill(2)} ~ {end_year}.{str(end_month).zfill(2)}"
    
    # Filter villa_txs to only include the last 6 months
    villa_6m_months = []
    for i in range(6):
        y = end_year
        m = end_month - i
        while m <= 0:
            m += 12
            y -= 1
        villa_6m_months.append((y, m))
        
    filtered_villa_txs = []
    for t in villa_txs:
        try:
            ty = int(t.get('dealYear', 0))
            tm = int(t.get('dealMonth', 0))
            if (ty, tm) in villa_6m_months:
                filtered_villa_txs.append(t)
        except:
            pass
    
    doc = SimpleDocTemplate(
        pdf_filename, 
        pagesize=A4, 
        rightMargin=40, 
        leftMargin=40, 
        topMargin=40, 
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        alignment=1, # Center
        spaceAfter=15,
        bold=True
    )
    
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=6,
        bold=True
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    
    table_hdr_style = ParagraphStyle(
        'TableHdr',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=8,
        leading=11,
        textColor=colors.white,
        alignment=1, # Center
        bold=True
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#334155')
    )
    
    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=table_cell_style,
        alignment=1
    )
    
    table_cell_count = ParagraphStyle(
        'TableCellCount',
        parent=table_cell_style,
        fontSize=7,
        leading=9,
        alignment=1
    )
    
    story = []
    
    # Top Header Office Info (Above Accent Bar)
    if member_info:
        header_left_style = ParagraphStyle(
            'HeaderLeft',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#4A5568')
        )
        header_right_style = ParagraphStyle(
            'HeaderRight',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#718096'),
            alignment=2 # Right
        )
        
        office_name = member_info.get("office_name") or member_info.get("office") or ""
        office_address = member_info.get("office_address") or ""
        phone = member_info.get("phone") or ""
        
        if phone == "01091280586" or "010-9128-0586" in phone or "신대림" in office_name:
            formatted_phone = "02-375-4489"
        else:
            formatted_phone = phone
            if phone:
                digits = "".join(filter(str.isdigit, phone))
                if len(digits) == 10:
                    formatted_phone = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
                elif len(digits) == 11:
                    formatted_phone = f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
                elif len(digits) == 9:
                    formatted_phone = f"{digits[:2]}-{digits[2:5]}-{digits[5:]}"
                
        header_left_text = f"<b>{office_name}</b>" if office_name else ""
        
        right_parts = []
        if office_address:
            right_parts.append(f"주소: {office_address}")
        if formatted_phone:
            right_parts.append(f"연락처: {formatted_phone}")
        header_right_text = "  |  ".join(right_parts)
        
        header_table_data = [[
            Paragraph(header_left_text, header_left_style),
            Paragraph(header_right_text, header_right_style)
        ]]
        header_table = Table(header_table_data, colWidths=[180, 335])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(header_table)
        
    # Top Accent Bar
    accent_bar = Table([[""]], colWidths=[515], rowHeights=[4])
    accent_bar.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(accent_bar)
    story.append(Spacer(1, 15))
    
    # Title
    story.append(Paragraph(f"📊 {region_prefix} {bjdong_nm} 부동산 동향 보고서", title_style))
    
    # Metadata Box
    meta_data = [
        [Paragraph("<b>분석 기준 지역</b>", body_style), Paragraph(f"{region_prefix} {bjdong_nm}", body_style)],
        [Paragraph("<b>분석 기준 기간</b>", body_style), Paragraph(f"아파트: 최근 24개월 ({period_str})<br/>연립/빌라: 최근 6개월 ({period_str_6})", body_style)],
        [Paragraph("<b>보고서 발행일</b>", body_style), Paragraph(datetime.now().strftime("%Y년 %m월 %d일"), body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[100, 415])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#475569')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))
    
    def build_prop_section(label, txs, prop_type):
        sect_story = []
        sect_story.append(Paragraph(f"■ {label} 시장 분석 동향", h2_style))
        
        if not txs:
            sect_story.append(Paragraph("최근 신고된 실거래 사례가 부족합니다.", body_style))
            sect_story.append(Spacer(1, 10))
            return sect_story
            
        trades = [t for t in txs if t.get('_trade_type') == '매매']
        jeonses = [t for t in txs if t.get('_trade_type') == '전세']
        wolses = [t for t in txs if t.get('_trade_type') == '월세']
        overall_rate = calculate_market_conversion_rate(txs)
        
        def get_avg_price(subset):
            prices = []
            for item in subset:
                val = str(item.get('dealAmount', '') or item.get('rowPrice', '') or item.get('deposit', '') or item.get('guaranteeAmt', '')).strip().replace(',', '')
                if val:
                    try:
                        prices.append(float(val))
                    except:
                        pass
            return sum(prices)/len(prices) if prices else None
            
        if prop_type == '2':
            # Villa specific grouped table
            groups = {
                "원룸형 (전용 20㎡ 미만)": [],
                "투룸형 (전용 20~40㎡)": [],
                "쓰리룸형 (전용 40~60㎡)": [],
                "대형 (전용 60㎡ 이상)": [],
                "지하층 (반지하 전체)": []
            }
            for t in txs:
                try:
                    if is_basement_transaction(t):
                        groups["지하층 (반지하 전체)"].append(t)
                        continue
                    area = float(t.get('excluUseAr', t.get('totalFloorAr', 0)))
                    if area > 0:
                        grp_name = get_villa_group(area)
                        groups[grp_name].append(t)
                except:
                    pass
            
            stat_data = [
                [
                    Paragraph("<b>구분 (방수 추정)</b>", table_hdr_style), 
                    Paragraph("<b>총 거래 건수</b>", table_hdr_style), 
                    Paragraph("<b>평균 매매가</b>", table_hdr_style), 
                    Paragraph("<b>평균 전세금<br/>(전세가율)</b>", table_hdr_style), 
                    Paragraph("<b>평균 전환율</b>", table_hdr_style)
                ]
            ]
            
            for grp_name in ["원룸형 (전용 20㎡ 미만)", "투룸형 (전용 20~40㎡)", "쓰리룸형 (전용 40~60㎡)", "대형 (전용 60㎡ 이상)", "지하층 (반지하 전체)"]:
                g_txs = groups[grp_name]
                g_trades = [t for t in g_txs if t.get('_trade_type') == '매매']
                g_jeonses = [t for t in g_txs if t.get('_trade_type') == '전세']
                g_wolses = [t for t in g_txs if t.get('_trade_type') == '월세']
                
                g_avg_trade = get_avg_price(g_trades)
                g_avg_jeonse = get_avg_price(g_jeonses)
                g_overall_rate = calculate_market_conversion_rate(g_txs)
                
                g_trade_str = local_format_price(g_avg_trade) if g_avg_trade else "-"
                if g_avg_jeonse:
                    if g_avg_trade:
                        g_j_rate = int(round(g_avg_jeonse / g_avg_trade * 100))
                        g_jeonse_str = f"{local_format_price(g_avg_jeonse)}<br/>({g_j_rate}%)"
                    else:
                        g_jeonse_str = local_format_price(g_avg_jeonse)
                else:
                    g_jeonse_str = "-"
                    
                g_rate_str = f"{g_overall_rate:.2f}%" if g_overall_rate else "-"
                
                count_p = Paragraph(
                    f"총 {len(g_txs)}건<br/><font size=6.5 color='#718096'>(매{len(g_trades)}/전{len(g_jeonses)}/월{len(g_wolses)})</font>", 
                    table_cell_center
                )
                
                stat_data.append([
                    Paragraph(grp_name, table_cell_center),
                    count_p,
                    Paragraph(g_trade_str, table_cell_center),
                    Paragraph(g_jeonse_str, table_cell_center),
                    Paragraph(g_rate_str, table_cell_center)
                ])
                
            stat_table = Table(stat_data, colWidths=[140, 95, 90, 100, 90])
            stat_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LINEABOVE', (0,0), (-1,0), 1, colors.HexColor('#0F172A')),
                ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#0F172A')),
                ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                ('LINEBELOW', (0,-1), (-1,-1), 1, colors.HexColor('#0F172A')),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ]))
            for idx in range(1, len(stat_data)):
                bg_color = colors.HexColor('#FFFFFF') if idx % 2 == 1 else colors.HexColor('#F7FAFC')
                stat_table.setStyle(TableStyle([('BACKGROUND', (0, idx), (-1, idx), bg_color)]))
        else:
            # Apartment specific table
            avg_trade = get_avg_price(trades)
            avg_jeonse = get_avg_price(jeonses)
            
            trade_str = local_format_price(avg_trade) if avg_trade else "거래 사례 없음"
            if avg_jeonse:
                if avg_trade:
                    j_rate = int(round(avg_jeonse / avg_trade * 100))
                    jeonse_str = f"{local_format_price(avg_jeonse)}<br/>(매매가 대비 {j_rate}%)"
                else:
                    jeonse_str = local_format_price(avg_jeonse)
            else:
                jeonse_str = "거래 사례 없음"
                
            rate_str = f"{overall_rate:.2f}%" if overall_rate else "산출 불가"
            
            stat_data = [
                [Paragraph("<b>구분</b>", table_hdr_style), Paragraph("<b>총 거래 건수</b>", table_hdr_style), Paragraph("<b>평균 매매가</b>", table_hdr_style), Paragraph("<b>평균 전세금 (전세가율)</b>", table_hdr_style), Paragraph("<b>평균 전월세전환율</b>", table_hdr_style)],
                [
                    Paragraph(label.split()[1], table_cell_center),
                    Paragraph(f"{len(txs)}건<br/>(매매 {len(trades)} / 전세 {len(jeonses)} / 월세 {len(wolses)})", table_cell_center),
                    Paragraph(trade_str, table_cell_center),
                    Paragraph(jeonse_str, table_cell_center),
                    Paragraph(rate_str, table_cell_center)
                ]
            ]
            stat_table = Table(stat_data, colWidths=[80, 110, 110, 110, 105])
            stat_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LINEABOVE', (0,0), (-1,0), 1, colors.HexColor('#0F172A')),
                ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#0F172A')),
                ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                ('LINEBELOW', (0,-1), (-1,-1), 1, colors.HexColor('#0F172A')),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ]))
            
        sect_story.append(stat_table)
        
        # Add room-count estimation footnote if it is Villa (prop_type == '2')
        if prop_type == '2':
            footnote_style = ParagraphStyle(
                'VillaFootnoteStyle',
                parent=styles['Normal'],
                fontName=font_name,
                fontSize=7.5,
                leading=11,
                textColor=colors.HexColor('#718096')
            )
            villa_footnote_text = (
                "※ <b>방수 추정 기준 안내</b>: 위 분류는 건축물대장상 실제 방 개수가 아닌, 전용면적별 주거 기준(법정 최소면적 및 일반적 방수별 면적)을 적용하여 분류한 추정치입니다. 실제 내부 구조와는 차이가 있을 수 있습니다. 지하층(반지하)은 지상층 면적별 집계에서 제외하고 별도 분리하여 통계 처리하였습니다."
            )
            sect_story.append(Spacer(1, 4))
            sect_story.append(Paragraph(villa_footnote_text, footnote_style))
            
        sect_story.append(Spacer(1, 8))
        
        # Segments table
        if overall_rate:
            seg_data = analyze_conversion_rate_segments(txs, prop_type)
            if seg_data:
                ths = seg_data['thresholds']
                t0_str = local_format_price(ths[0]).replace(' ', '')
                t1_str = local_format_price(ths[1]).replace(' ', '')
                
                g1_val = f"{seg_data['g1_rate']:.2f}% ({seg_data['g1_count']}건)" if seg_data['g1_rate'] else "데이터 없음"
                g2_val = f"{seg_data['g2_rate']:.2f}% ({seg_data['g2_count']}건)" if seg_data['g2_rate'] else "데이터 없음"
                g3_val = f"{seg_data['g3_rate']:.2f}% ({seg_data['g3_count']}건)" if seg_data['g3_rate'] else "데이터 없음"
                
                seg_table_data = [
                    [Paragraph("<b>보증금 구간</b>", table_hdr_style), Paragraph("<b>평균 전월세 전환율 (실거래 건수)</b>", table_hdr_style)],
                    [Paragraph(f"소액 보증금 ({t0_str} 미만)", table_cell_center), Paragraph(g1_val, table_cell_center)],
                    [Paragraph(f"중소 보증금 ({t0_str} ~ {t1_str} 미만)", table_cell_center), Paragraph(g2_val, table_cell_center)],
                    [Paragraph(f"고액 보증금 ({t1_str} 이상)", table_cell_center), Paragraph(g3_val, table_cell_center)],
                ]
                seg_table = Table(seg_table_data, colWidths=[200, 315])
                seg_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('LINEABOVE', (0,0), (-1,0), 1, colors.HexColor('#1E293B')),
                    ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#1E293B')),
                    ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                    ('LINEBELOW', (0,-1), (-1,-1), 1, colors.HexColor('#1E293B')),
                    ('TOPPADDING', (0,0), (-1,-1), 5),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                    ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#FFFFFF')),
                    ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#F8FAFC')),
                    ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#FFFFFF')),
                ]))
                sect_story.append(Paragraph("<b>• 보증금 구간별 전월세 전환율 분포</b>", body_style))
                sect_story.append(Spacer(1, 4))
                sect_story.append(seg_table)
                sect_story.append(Spacer(1, 4))
                
                footnote_style = ParagraphStyle(
                    'FootnoteStyle',
                    parent=styles['Normal'],
                    fontName=font_name,
                    fontSize=7.5,
                    leading=11,
                    textColor=colors.HexColor('#718096')
                )
                footnote_text = (
                    f"※ <b>보증금 구간 기준 안내</b>: 위 표의 '보증금 구간'은 전환 금액이 아닌, 월세 계약의 <b>'최종 월세 보증금'</b> 기준입니다. "
                    f"예를 들어, 기존 전세 4억 5천만원 중 5천만원을 보증금으로 두고 나머지 4억원을 월세로 바꿀 때는 "
                    f"최종 월세 보증금이 5천만원이 되므로 <b>'중소 보증금 ({t0_str} ~ {t1_str} 미만)'</b> 구간의 전환율이 적용됩니다."
                )
                sect_story.append(Paragraph(footnote_text, footnote_style))
                sect_story.append(Spacer(1, 10))
        return sect_story
        
    # Add main sections
    story.extend(build_prop_section("🏢 아파트 (최근 24개월 기준)", filtered_apt_txs, '1'))
    
    # Representative Apartment section
    if apt_txs:
        if not rep_apt_name:
            apt_counts = {}
            for t in filtered_apt_txs:
                name = t.get('aptNm')
                if name:
                    apt_counts[name] = apt_counts.get(name, 0) + 1
            if apt_counts:
                rep_apt_name = max(apt_counts, key=apt_counts.get)
        
        if rep_apt_name:
            rep_count = sum(1 for t in apt_txs if t.get('aptNm') == rep_apt_name)
            
            story.append(Paragraph(f"■ 대표 지표 아파트 단지 상세 분석: <b>{rep_apt_name}</b>", h2_style))
            story.append(Spacer(1, 5))
            
            # Draw chart if trend_data is provided
            if trend_data:
                chart_drawing = create_trend_chart_drawing(trend_data, rep_apt_name)
                story.append(chart_drawing)
                story.append(Spacer(1, 10))
                
            if rep_count > 0:
                story.append(Paragraph(f"• 최근 24개월 ({period_str}) 실거래 건수: 총 {rep_count}건", body_style))
            else:
                story.append(Paragraph(f"• 지정된 지표 아파트 단지 분석 정보입니다.", body_style))
            story.append(Spacer(1, 5))
            
            rep_txs = [t for t in apt_txs if t.get('aptNm') == rep_apt_name]
            groups = {}
            for t in rep_txs:
                try:
                    ar = float(t.get('excluUseAr'))
                    pyung = estimate_supply_pyung(ar)
                    groups.setdefault(pyung, []).append(t)
                except:
                    pass
                    
            apt_headers = [
                Paragraph("<b>평형</b>", table_hdr_style),
                Paragraph("<b>전용면적</b>", table_hdr_style),
                Paragraph("<b>평균 매매가</b>", table_hdr_style),
                Paragraph("<b>평균 전세금<br/>(전세가율)</b>", table_hdr_style),
                Paragraph("<b>평균 월세 (보증금/월세)</b>", table_hdr_style),
                Paragraph("<b>거래 건수</b>", table_hdr_style)
            ]
            apt_table_rows = [apt_headers]
            
            for pyung in sorted(groups.keys()):
                g_txs = groups[pyung]
                trades = [t for t in g_txs if t.get('_trade_type') == '매매']
                jeonses = [t for t in g_txs if t.get('_trade_type') == '전세']
                wolses = [t for t in g_txs if t.get('_trade_type') == '월세']
                
                def get_avg(subset):
                    prices = []
                    for item in subset:
                        val = str(item.get('dealAmount', '') or item.get('deposit', '') or item.get('guaranteeAmt', '')).strip().replace(',', '')
                        if val:
                            try: prices.append(float(val))
                            except: pass
                    return sum(prices)/len(prices) if prices else None
                    
                avg_t = get_avg(trades)
                avg_j = get_avg(jeonses)
                avg_w_dep = get_avg(wolses)
                
                w_rents = []
                for w in wolses:
                    val = str(w.get('monthlyRent', '') or w.get('monthly', '')).strip().replace(',', '')
                    if val:
                        try: w_rents.append(float(val))
                        except: pass
                avg_w_rent = sum(w_rents)/len(w_rents) if w_rents else None
                
                t_str = local_format_price(avg_t) if avg_t else '-'
                if avg_j:
                    if avg_t:
                        j_rate = int(round(avg_j / avg_t * 100))
                        j_str = f"{local_format_price(avg_j)}<br/>({j_rate}%)"
                    else:
                        j_str = local_format_price(avg_j)
                else:
                    j_str = '-'
                w_str = f"{local_format_price(avg_w_dep)}/{int(avg_w_rent)}만" if (avg_w_dep and avg_w_rent) else '-'
                
                avg_area = sum([float(t.get('excluUseAr')) for t in g_txs]) / len(g_txs)
                
                apt_table_rows.append([
                    Paragraph(f"{pyung}평형", table_cell_center),
                    Paragraph(f"전용 {avg_area:.1f}㎡", table_cell_center),
                    Paragraph(t_str, table_cell_center),
                    Paragraph(j_str, table_cell_center),
                    Paragraph(w_str, table_cell_center),
                    Paragraph(f"총 {len(g_txs)}건<br/>(매{len(trades)}/전{len(jeonses)}/월{len(wolses)})", table_cell_count)
                ])
                
            apt_rep_table = Table(apt_table_rows, colWidths=[60, 80, 95, 95, 100, 85])
            apt_rep_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LINEABOVE', (0,0), (-1,0), 1, colors.HexColor('#0F172A')),
                ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#0F172A')),
                ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                ('LINEBELOW', (0,-1), (-1,-1), 1, colors.HexColor('#0F172A')),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ]))
            
            for idx in range(1, len(apt_table_rows)):
                bg_color = colors.HexColor('#FFFFFF') if idx % 2 == 1 else colors.HexColor('#F7FAFC')
                apt_rep_table.setStyle(TableStyle([('BACKGROUND', (0, idx), (-1, idx), bg_color)]))
                
            story.append(apt_rep_table)
            story.append(Spacer(1, 10))
            
    # Add Villa sections
    story.extend(build_prop_section("🏡 연립/다세대/빌라 (최근 6개월 기준)", filtered_villa_txs, '2'))
    
    # 정밀 시세 분석(CMA) 및 상담 안내 (CTA)
    if member_info:
        cta_title_style = ParagraphStyle(
            'CtaTitle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#1E293B'),
            bold=True,
            spaceBefore=12,
            spaceAfter=5
        )
        cta_body_style = ParagraphStyle(
            'CtaBody',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=8,
            leading=12,
            textColor=colors.HexColor('#475569')
        )
        cta_text = (
            "본 보고서는 해당 지역의 표준적인 실거래 데이터를 기반으로 한 통계 분석 리포트입니다. "
            "개별 세대의 인테리어 상태, 조망권, 일조량 및 동·호수별 위치에 따른 정밀한 개별 자산 가치(CMA) 분석이나 "
            "정확한 매도/임대 시세 평가가 필요하신 소유자분께서는 본 보고서를 발행한 아래 담당 파트너 중개사에 문의하시면 "
            "상세한 자산 진단 및 맞춤형 정밀 시세 리포트를 무료로 제공받으실 수 있습니다."
        )
        story.append(Spacer(1, 10))
        story.append(Paragraph("■ 자산 가치 평가 및 정밀 시세(CMA) 상담 안내", cta_title_style))
        
        cta_box = Table([[Paragraph(cta_text, cta_body_style)]], colWidths=[515])
        cta_box.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(cta_box)

    # Broker Signature Block
    if member_info:
        story.append(Spacer(1, 10))
        sig_title_style = ParagraphStyle(
            'SigTitle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#1E293B'),
            bold=True,
            spaceAfter=5
        )
        
        # Add analyst job title to broker name
        broker_name = member_info.get('name', '')
        formatted_broker_name = f"{broker_name} (지역 담당 자문 공인중개사)" if broker_name else "-"
        
        story.append(Paragraph("■ 담당 분석 및 자문 공인중개사", sig_title_style))
        
        sig_phone = member_info.get("phone", "-")
        if sig_phone == "01091280586" or sig_phone == "010-9128-0586":
            sig_phone = "02-375-4489 (HP: 010-9128-0586)"
        else:
            if sig_phone and sig_phone != "-":
                digits = "".join(filter(str.isdigit, sig_phone))
                if len(digits) == 10:
                    sig_phone = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
                elif len(digits) == 11:
                    sig_phone = f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
                elif len(digits) == 9:
                    sig_phone = f"{digits[:2]}-{digits[2:5]}-{digits[5:]}"

        sig_reg = member_info.get("registration_number") or "92380000-4131"

        sig_data = [
            [
                Paragraph("<b>중개사무소명</b>", body_style), 
                Paragraph(member_info.get("office_name") or member_info.get("office", "중개수첩 회원 공인중개사사무소"), body_style),
                Paragraph("<b>등록번호</b>", body_style),
                Paragraph(sig_reg, body_style)
            ],
            [
                Paragraph("<b>담당 공인중개사</b>", body_style),
                Paragraph(formatted_broker_name, body_style),
                Paragraph("<b>중개의뢰 및 문의</b>", body_style),
                Paragraph(sig_phone, body_style)
            ],
            [
                Paragraph("<b>사무소 주소</b>", body_style),
                Paragraph(member_info.get("office_address", "-"), body_style),
                "",
                ""
            ]
        ]
        sig_table = Table(sig_data, colWidths=[80, 170, 95, 170])
        sig_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#475569')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('SPAN', (1, 2), (3, 2)),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(sig_table)
        
    # Disclaimer Box
    story.append(Spacer(1, 10))
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=7,
        leading=10,
        textColor=colors.HexColor('#718096')
    )
    disclaimer_text = (
        "• 본 보고서는 국토교통부 실거래공개시스템의 실거래가 자료를 기초로 자동 계산된 통계 분석 정보입니다.<br/>"
        "• 주택법 및 시세 변동 요인에 따라 개별 매물의 실제 가치와는 상이할 수 있으며, 어떠한 법적 분쟁의 증빙 자료로도 사용될 수 없습니다."
    )
    disclaimer_table = Table([[Paragraph(disclaimer_text, disclaimer_style)]], colWidths=[515])
    disclaimer_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(disclaimer_table)
    
    doc.build(story)

def run_market_analysis():
    print("==================================================")
    print("      동네별 부동산 시장 동향 및 전월세 분석      ")
    print("==================================================")
    
    dong_input = input("분석할 동 이름을 입력하세요 (예: 성산동, 수색동, 망원동): ").strip()
    if not dong_input:
        return
        
    # Clean up input dynamically (keep numbers initially for administrative dongs)
    clean_dong = dong_input
    words = clean_dong.split()
    if words:
        last_word = words[-1]
        if not (last_word.endswith('동') or last_word.endswith('가') or last_word.endswith('리') or last_word.endswith('로') or last_word.endswith('길')):
            words[-1] = last_word + '동'
        clean_dong = " ".join(words)
        
    # Determine default region prefix from member_info if available
    member_info = load_member_info()
    default_prefix = "서울특별시 마포구"
    if member_info and member_info.get("office_address"):
        addr_parts = member_info["office_address"].split()
        if len(addr_parts) >= 2:
            default_prefix = f"{addr_parts[0]} {addr_parts[1]}"
            
    # Check if the input already contains regional terms
    has_region = False
    for word in clean_dong.split():
        if word.endswith('시') or word.endswith('도') or word.endswith('구') or word.endswith('군'):
            has_region = True
            break
            
    if has_region:
        search_query = clean_dong
    else:
        search_query = f"{default_prefix} {clean_dong}"
        
    print(f"\n -> 주소 확인 및 코드 조회 중: {search_query}...")
    addr_info = get_kakao_address_info(search_query)
    
    # Fallback with numeric stripping if initial search fails (e.g. if they typed a typo or non-existent administrative name)
    if not addr_info:
        fallback_dong = re.sub(r'\s*\d+\s*동$', '동', clean_dong)
        if has_region:
            search_query = fallback_dong
        else:
            search_query = f"{default_prefix} {fallback_dong}"
        print(f" -> '{dong_input}' 검색 실패. '{search_query}'(으)로 재시도 중...")
        addr_info = get_kakao_address_info(search_query)
        
    if not addr_info:
        print(" [!] 주소 변환 실패! 올바른 동 이름을 입력해주세요.")
        return
        
    bjdong_nm = addr_info['bjdongNm']
    sigunguCd = addr_info['sigunguCd']
    sido_nm = addr_info.get('sidoNm', '')
    sigungu_nm = addr_info.get('sigunguNm', '')
    full_region_name = f"{sido_nm} {sigungu_nm}" if (sido_nm and sigungu_nm) else default_prefix
    
    # Resolve administrative/legal dong mapping
    matched_group = None
    norm_input = clean_dong.replace(" ", "")
    for k in DONG_GROUPS.keys():
        if norm_input == k or norm_input.replace("동", "") == k.replace("동", ""):
            matched_group = DONG_GROUPS[k]
            break
            
    if matched_group:
        target_dongs = matched_group["dongs"]
        display_dong_name = matched_group["display"]
    else:
        target_dongs = [bjdong_nm]
        display_dong_name = bjdong_nm
        
        matched_group = DONG_GROUPS.get(bjdong_nm)
        if matched_group:
            target_dongs = matched_group["dongs"]
            display_dong_name = matched_group["display"]
        else:
            # Fallback numeric cleanup: if user typed "수색1동", strip the number for legal querying but keep display name
            clean_name = re.sub(r'\s*\d+\s*동$', '동', bjdong_nm)
            if clean_name != bjdong_nm:
                target_dongs = [clean_name]
                display_dong_name = bjdong_nm
            
    file_safe_dong = display_dong_name.replace(' ', '_').replace('(', '').replace(')', '').replace(',', '')
    
    # Calculate 24-month period range dynamically
    now = datetime.now()
    end_year = now.year
    end_month = now.month
    start_month = end_month - 23
    start_year = end_year
    while start_month <= 0:
        start_month += 12
        start_year -= 1
    period_str = f"{start_year}.{str(start_month).zfill(2)} ~ {end_year}.{str(end_month).zfill(2)}"
    
    # Calculate 6-month period range dynamically
    start_month_6 = end_month - 5
    start_year_6 = end_year
    while start_month_6 <= 0:
        start_month_6 += 12
        start_year_6 -= 1
    period_str_6 = f"{start_year_6}.{str(start_month_6).zfill(2)} ~ {end_year}.{str(end_month).zfill(2)}"
    
    print(f" -> 법정동 확인: {full_region_name} {', '.join(target_dongs)} (시군구코드: {sigunguCd})")
    print(f" -> 최근 24개월 ({period_str}) 실거래 데이터를 수집하는 중입니다 (병렬 처리)...")
    
    # Fetch data for all target dongs and merge
    apt_txs = []
    villa_txs = []
    has_timeout = False
    has_auth_error = False
    
    for tdong in target_dongs:
        try:
            apt_res = get_recent_transactions(sigunguCd, '', '', '1', bjdong_nm=tdong, expand_similar=True)
            if apt_res is None:
                has_auth_error = True
            else:
                apt_txs.extend(apt_res)
                if getattr(apt_res, "connection_timeout_error", False):
                    has_timeout = True
                if getattr(apt_res, "trade_permission_error", False) or getattr(apt_res, "rent_permission_error", False):
                    has_auth_error = True
                    
            villa_res = get_recent_transactions(sigunguCd, '', '', '2', bjdong_nm=tdong, expand_similar=True)
            if villa_res is None:
                has_auth_error = True
            else:
                villa_txs.extend(villa_res)
                if getattr(villa_res, "connection_timeout_error", False):
                    has_timeout = True
                if getattr(villa_res, "trade_permission_error", False) or getattr(villa_res, "rent_permission_error", False):
                    has_auth_error = True
        except Exception as e:
            print(f" -> {tdong} 데이터 수집 중 오류: {e}")
            
    # ── 행정동 필터링 (생활권 단위 일치) ──
    target_admin_dong = None
    norm_input = clean_dong.replace(" ", "")
    if re.search(r'\d+동$', norm_input):
        target_admin_dong = norm_input
    else:
        if matched_group:
            for k in DONG_GROUPS.keys():
                if norm_input == k or norm_input.replace("동", "") == k.replace("동", ""):
                    if re.search(r'\d+동$', k):
                        target_admin_dong = k
                    break

    if target_admin_dong:
        norm_target_admin = normalize_h_dong_name(target_admin_dong)
        print(f" -> 행정동 필터링 활성화: {target_admin_dong} 관할 주소 매물만 추출합니다...")
        
        def filter_by_h_dong(tx_list):
            if not tx_list:
                return tx_list
            unique_keys = set()
            for t in tx_list:
                bjdong = t.get('umdNm') or t.get('dong') or ""
                jibun = t.get('jibun') or ""
                if bjdong and jibun:
                    unique_keys.add((str(bjdong).strip(), str(jibun).strip()))
                    
            h_dong_map = {}
            def resolve_one(key):
                bjdong, jibun = key
                h_dong = get_cached_admin_dong(full_region_name, bjdong, jibun)
                return key, h_dong
                
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
                res = executor.map(resolve_one, unique_keys)
                for key, h_dong in res:
                    h_dong_map[key] = h_dong
                    
            filtered = []
            for t in tx_list:
                bjdong = str(t.get('umdNm') or t.get('dong') or "").strip()
                jibun = str(t.get('jibun') or "").strip()
                h_dong = h_dong_map.get((bjdong, jibun), "")
                
                if h_dong:
                    if normalize_h_dong_name(h_dong) == norm_target_admin:
                        filtered.append(t)
                else:
                    filtered.append(t)
            return filtered

        apt_txs = filter_by_h_dong(apt_txs)
        villa_txs = filter_by_h_dong(villa_txs)
            
    # ── 아파트 단지 필터링 (시세 왜곡 방지) ──
    filtered_apt_txs = list(apt_txs)
    if apt_txs:
        apt_counts = {}
        for t in apt_txs:
            name = t.get('aptNm')
            if name:
                apt_counts[name] = apt_counts.get(name, 0) + 1
        
        if apt_counts:
            sorted_apts = sorted(apt_counts.items(), key=lambda x: x[1], reverse=True)
            print("\n" + "="*50)
            print(" 🏢 [아파트 통계 필터링 (시세 왜곡 방지)]")
            print(" 평균가 계산에 포함할 아파트 단지를 선택해 주세요.")
            print(" (재건축 단지 등 시세 왜곡을 유발하는 단지는 제외하는 것을 권장합니다.)")
            print("-" * 50)
            for idx, (name, count) in enumerate(sorted_apts):
                print(f" [{idx+1}] {name} (총 {count}건)")
            print("="*50)
            print(" * 입력 방법:")
            print("   - 엔터(Enter): 모든 아파트 포함 (기본값)")
            print("   - 1,2,3 : 1번, 2번, 3번 아파트만 '포함' (나머지 제외)")
            print("   - -1,-2 : 1번, 2번 아파트만 '제외' (나머지 포함)")
            print("-" * 50)
            
            filter_input = input(" 선택할 번호를 입력하세요: ").strip()
            
            excluded_names = set()
            included_names = set()
            
            if filter_input:
                try:
                    parts = [p.strip() for p in filter_input.split(',')]
                    is_exclude = all(p.startswith('-') for p in parts if p)
                    
                    if is_exclude:
                        for p in parts:
                            if not p:
                                continue
                            val = int(p.replace('-', '').strip()) - 1
                            if 0 <= val < len(sorted_apts):
                                excluded_names.add(sorted_apts[val][0])
                        
                        if excluded_names:
                            candidate_txs = [t for t in apt_txs if t.get('aptNm') not in excluded_names]
                            if not candidate_txs:
                                print(" -> [주의] 선택하신 단지를 제외하면 아파트 데이터가 전혀 남지 않습니다. 필터를 적용하지 않습니다.")
                            else:
                                filtered_apt_txs = candidate_txs
                                print(f" -> 제외 단지: {', '.join(excluded_names)}")
                    else:
                        for p in parts:
                            if not p:
                                continue
                            val = int(p.strip()) - 1
                            if 0 <= val < len(sorted_apts):
                                included_names.add(sorted_apts[val][0])
                        
                        if included_names:
                            candidate_txs = [t for t in apt_txs if t.get('aptNm') in included_names]
                            if not candidate_txs:
                                print(" -> [주의] 선택하신 단지에 데이터가 없습니다. 필터를 적용하지 않습니다.")
                            else:
                                filtered_apt_txs = candidate_txs
                                print(f" -> 포함 단지: {', '.join(included_names)}")
                except Exception as e:
                    print(f" -> 입력 파싱 중 오류가 발생하여 모든 단지를 포함합니다: {e}")
                    
    report_lines = []
    
    def add_line(text=""):
        print(text)
        report_lines.append(text)
        
    # Filter villa_txs to only include the last 6 months for the console/TXT report
    villa_6m_months = []
    for i in range(6):
        y = end_year
        m = end_month - i
        while m <= 0:
            m += 12
            y -= 1
        villa_6m_months.append((y, m))
        
    filtered_villa_txs = []
    for t in villa_txs:
        try:
            ty = int(t.get('dealYear', 0))
            tm = int(t.get('dealMonth', 0))
            if (ty, tm) in villa_6m_months:
                filtered_villa_txs.append(t)
        except:
            pass

    add_line("\n" + "="*60)
    add_line(f" 📊 {display_dong_name} 부동산 시장 분석 보고서")
    add_line(f"   - 아파트: 최근 24개월 ({period_str})")
    add_line(f"   - 연립/빌라: 최근 6개월 ({period_str_6})")
    add_line(f"   - 분석 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    add_line(f"   - 대상 지역: {full_region_name} {display_dong_name}")
    add_line("="*60)
    
    if has_timeout:
        add_line("\n" + "!"*60)
        add_line(" ⚠️ [주의] 국토교통부 실거래가 API 서버 응답 지연/장애 발생")
        add_line("   현재 정부 공공데이터포털 서버(apis.data.go.kr)와의 통신이 원활하지")
        add_line("   않습니다. 일부 또는 전체 실거래 정보 수집에 실패하여 데이터가")
        add_line("   비정상적으로 적거나 존재하지 않는 것으로 표시될 수 있습니다.")
        add_line("   잠시 후 다시 시도해 주세요.")
        add_line("!"*60)
    
    # 1. Main sections
    for label, txs, prop_type in [("🏢 아파트 (최근 24개월 기준)", filtered_apt_txs, '1')]:
        if not txs:
            add_line(f"\n[{label}] 실거래 데이터가 존재하지 않습니다.")
            continue
            
        trades = [t for t in txs if t.get('_trade_type') == '매매']
        jeonses = [t for t in txs if t.get('_trade_type') == '전세']
        wolses = [t for t in txs if t.get('_trade_type') == '월세']
        
        def get_avg_price(subset):
            prices = []
            for item in subset:
                val = str(item.get('dealAmount', '') or item.get('rowPrice', '') or item.get('deposit', '') or item.get('guaranteeAmt', '')).strip().replace(',', '')
                if val:
                    try:
                        prices.append(float(val))
                    except:
                        pass
            return sum(prices)/len(prices) if prices else None
            
        avg_trade = get_avg_price(trades)
        avg_jeonse = get_avg_price(jeonses)
        
        add_line(f"\n[{label} 시장 동향]")
        add_line(f" • 총 실거래 건수: {len(txs):,}건 (매매 {len(trades):,}건 / 전세 {len(jeonses):,}건 / 월세 {len(wolses):,}건)")
        if avg_trade:
            add_line(f" • 평균 매매 거래가: {local_format_price(avg_trade)}")
        if avg_jeonse:
            if avg_trade:
                j_rate = int(round(avg_jeonse / avg_trade * 100))
                add_line(f" • 평균 전세 보증금: {local_format_price(avg_jeonse)} (매매가 대비 {j_rate}%)")
            else:
                add_line(f" • 평균 전세 보증금: {local_format_price(avg_jeonse)}")
            
        overall_rate = calculate_market_conversion_rate(txs)
        if overall_rate:
            add_line(f" • 평균 전월세 전환율: {overall_rate:.2f}%")
            
            seg_data = analyze_conversion_rate_segments(txs, prop_type)
            if seg_data:
                ths = seg_data['thresholds']
                add_line(" • 보증금 구간별 전월세 전환율 상세:")
                
                t0_str = local_format_price(ths[0]).replace(' ', '')
                t1_str = local_format_price(ths[1]).replace(' ', '')
                
                if seg_data['g1_rate']:
                    add_line(f"   - 소액 보증금 ({t0_str} 미만): {seg_data['g1_rate']:.2f}% ({seg_data['g1_count']}건)")
                if seg_data['g2_rate']:
                    add_line(f"   - 중소 보증금 ({t0_str} ~ {t1_str} 미만): {seg_data['g2_rate']:.2f}% ({seg_data['g2_count']}건)")
                if seg_data['g3_rate']:
                    add_line(f"   - 고액 보증금 ({t1_str} 이상): {seg_data['g3_rate']:.2f}% ({seg_data['g3_count']}건)")
                add_line(f"   ※ 안내: '보증금 구간'은 전환 금액이 아닌 월세 계약의 '최종 월세 보증금' 기준입니다. (예: 전세 4.5억 중 5천을 보증금으로 두고 전환 시 '중소 보증금' 구간 전환율 적용)")
        else:
            add_line(" • 전월세 전환율: 분석을 위한 전세/월세 데이터 매칭 사례 부족")
            
        add_line("-" * 50)
        
    # Representative Apartment section (Console)
    rep_apt_name = None
    trend_data = None
    
    if apt_txs:
        apt_counts = {}
        for t in apt_txs:
            name = t.get('aptNm')
            if name:
                apt_counts[name] = apt_counts.get(name, 0) + 1
        
        if apt_counts:
            sorted_apts = sorted(apt_counts.items(), key=lambda x: x[1], reverse=True)
            print("\n" + "="*50)
            print(" 🏢 [지표 아파트 단지 선택]")
            print(f" 최근 24개월 ({period_str}) 이 법정동에서 거래가 많았던 아파트 단지 목록입니다:")
            for idx, (name, count) in enumerate(sorted_apts[:5]):
                print(f" {idx+1}. {name} (총 {count}건)")
            print(" *. 직접 입력 (원하는 다른 아파트명을 입력)")
            print("="*50)
            
            sel = input(" 분석할 지표 아파트를 선택해 주세요 (번호 또는 아파트명 직접 입력, 기본값: 1): ").strip()
            
            if not sel:
                rep_apt_name = sorted_apts[0][0]
            elif sel.isdigit():
                sel_idx = int(sel) - 1
                if 0 <= sel_idx < len(sorted_apts):
                    rep_apt_name = sorted_apts[sel_idx][0]
                else:
                    print(f"  [!] 잘못된 번호입니다. 가장 거래가 많은 '{sorted_apts[0][0]}' 단지를 선택합니다.")
                    rep_apt_name = sorted_apts[0][0]
            else:
                rep_apt_name = sel
                
            matched_name = None
            rep_clean = rep_apt_name.lower().replace("아파트", "").replace(" ", "").strip()
            
            # Step 1: Exact match ignoring space and "아파트" suffix
            for name in apt_counts.keys():
                name_clean = name.lower().replace("아파트", "").replace(" ", "").strip()
                if rep_clean == name_clean:
                    matched_name = name
                    break
                    
            # Step 2: Search term is a substring of target name
            if not matched_name:
                for name in apt_counts.keys():
                    name_clean = name.lower().replace("아파트", "").replace(" ", "").strip()
                    if rep_clean in name_clean:
                        matched_name = name
                        break
                        
            # Step 3: Key words match for specific complexes like "대림월드타운" -> "성산월드타운대림"
            if not matched_name:
                for name in apt_counts.keys():
                    name_clean = name.lower()
                    if "대림" in name_clean and ("월드타운" in name_clean or "월드" in name_clean):
                        matched_name = name
                        break
                        
            if matched_name:
                rep_apt_name = matched_name
                
            rep_count = apt_counts.get(rep_apt_name, 0)
            
            add_line(f"\n[🏢 대표 지표 아파트 단지 상세 분석: {rep_apt_name}]")
                
            trend_data = []
            rep_txs_trade = [t for t in apt_txs if t.get('aptNm') == rep_apt_name and t.get('_trade_type') == '매매']
            rep_txs_jeonse = [t for t in apt_txs if t.get('aptNm') == rep_apt_name and t.get('_trade_type') == '전세']
            
            trend_txs = []
            for t in rep_txs_trade:
                try:
                    ar = float(t.get('excluUseAr'))
                    pyung = estimate_supply_pyung(ar)
                    if 30 <= pyung <= 39:
                        trend_txs.append(t)
                except:
                    pass
                    
            trend_jeonse_txs = []
            for t in rep_txs_jeonse:
                try:
                    ar = float(t.get('excluUseAr'))
                    pyung = estimate_supply_pyung(ar)
                    if 30 <= pyung <= 39:
                        trend_jeonse_txs.append(t)
                except:
                    pass
                    
            now = datetime.now()
            # Shift the trend period to end at 2 months ago due to the 30-day reporting lag
            current_year = now.year
            current_month = now.month
            months_chrono = []
            for i in range(13, 1, -1):
                year = current_year
                month = current_month - i
                while month <= 0:
                    month += 12
                    year -= 1
                months_chrono.append((year, month, f"{year}-{str(month).zfill(2)}"))
                
            for year, month, month_str in months_chrono:
                # 매매 집계
                month_txs = []
                for t in trend_txs:
                    try:
                        t_year = int(t.get('dealYear'))
                        t_month = int(t.get('dealMonth'))
                        if t_year == year and t_month == month:
                            month_txs.append(t)
                    except:
                        pass
                prices = []
                for t in month_txs:
                    val = str(t.get('dealAmount', '')).strip().replace(',', '')
                    if val:
                        try: prices.append(float(val))
                        except: pass
                avg_price = sum(prices) / len(prices) if prices else None
                
                # 전세 집계
                month_jeonse_txs = []
                for t in trend_jeonse_txs:
                    try:
                        t_year = int(t.get('dealYear'))
                        t_month = int(t.get('dealMonth'))
                        if t_year == year and t_month == month:
                            month_jeonse_txs.append(t)
                    except:
                        pass
                j_prices = []
                for t in month_jeonse_txs:
                    val = str(t.get('deposit', '') or t.get('guaranteeAmt', '')).strip().replace(',', '')
                    if val:
                        try: j_prices.append(float(val))
                        except: pass
                avg_jeonse_price = sum(j_prices) / len(j_prices) if j_prices else None
                
                short_month = f"{str(year)[2:]}.{str(month).zfill(2)}"
                trend_data.append({
                    'month': short_month,
                    'avg': avg_price,
                    'count': len(prices),
                    'jeonse_avg': avg_jeonse_price,
                    'jeonse_count': len(j_prices)
                })
                
            # Calculate 12-month period range dynamically (ending 2 months ago due to reporting lag)
            now = datetime.now()
            end_month = now.month - 2
            end_year = now.year
            while end_month <= 0:
                end_month += 12
                end_year -= 1
            start_month = now.month - 13
            start_year = now.year
            while start_month <= 0:
                start_month += 12
                start_year -= 1
            trend_period_str = f"{start_year}.{str(start_month).zfill(2)} ~ {end_year}.{str(end_month).zfill(2)}"

            has_trend_data = any(item['avg'] is not None or item.get('jeonse_avg') is not None for item in trend_data)
            if has_trend_data:
                add_line(f"\n📈 [{rep_apt_name} 30평대 매매 및 전세 평균가 추이 (최근 12개월: {trend_period_str})]")
                for item in trend_data:
                    m = item['month']
                    avg_val = item['avg']
                    cnt = item['count']
                    jeonse_val = item.get('jeonse_avg')
                    jeonse_cnt = item.get('jeonse_count', 0)
                    
                    trade_display = local_format_price(avg_val) if avg_val is not None else "-"
                    jeonse_display = local_format_price(jeonse_val) if jeonse_val is not None else "-"
                    
                    add_line(f"   {m} | 매매: {trade_display:<9s} ({cnt}건) | 전세: {jeonse_display:<9s} ({jeonse_cnt}건)")
                add_line("-" * 50)
            
            if rep_count > 0:
                add_line(f" • 최근 24개월 ({period_str}) 이 법정동 내 실거래 건수: 총 {rep_count}건")
            else:
                add_line(f" • 입력하신 단지는 최근 실거래 내역에 포함되어 있지 않거나 직접 지정되었습니다.")
                
            rep_txs_all = [t for t in apt_txs if t.get('aptNm') == rep_apt_name]
            groups = {}
            for t in rep_txs_all:
                try:
                    ar = float(t.get('excluUseAr'))
                    pyung = estimate_supply_pyung(ar)
                    groups.setdefault(pyung, []).append(t)
                except:
                    pass
            
            for pyung in sorted(groups.keys()):
                g_txs = groups[pyung]
                trades = [t for t in g_txs if t.get('_trade_type') == '매매']
                jeonses = [t for t in g_txs if t.get('_trade_type') == '전세']
                wolses = [t for t in g_txs if t.get('_trade_type') == '월세']
                
                def get_avg(subset):
                    prices = []
                    for item in subset:
                        val = str(item.get('dealAmount', '') or item.get('deposit', '') or item.get('guaranteeAmt', '')).strip().replace(',', '')
                        if val:
                            try: prices.append(float(val))
                            except: pass
                    return sum(prices)/len(prices) if prices else None
                    
                avg_t = get_avg(trades)
                avg_j = get_avg(jeonses)
                avg_w_dep = get_avg(wolses)
                
                w_rents = []
                for w in wolses:
                    val = str(w.get('monthlyRent', '') or w.get('monthly', '')).strip().replace(',', '')
                    if val:
                        try: w_rents.append(float(val))
                        except: pass
                avg_w_rent = sum(w_rents)/len(w_rents) if w_rents else None
                
                t_str = local_format_price(avg_t) if avg_t else '-'
                if avg_j:
                    if avg_t:
                        j_rate = int(round(avg_j / avg_t * 100))
                        j_str = f"{local_format_price(avg_j)} ({j_rate}%)"
                    else:
                        j_str = local_format_price(avg_j)
                else:
                    j_str = '-'
                w_str = f"{local_format_price(avg_w_dep)}/{int(avg_w_rent)}만" if (avg_w_dep and avg_w_rent) else '-'
                
                avg_area = sum([float(t.get('excluUseAr')) for t in g_txs]) / len(g_txs)
                
                add_line(f" • {pyung:2d}평형 (전용 {avg_area:.1f}㎡): 매매 {t_str:10s} | 전세 {j_str:18s} | 월세 {w_str} (총 {len(g_txs)}건: 매매 {len(trades)}/전세 {len(jeonses)}/월세 {len(wolses)})")
            add_line("-" * 50)
            
    # Villa section
    for label, txs, prop_type in [("🏡 연립/다세대/빌라 (최근 6개월 기준)", filtered_villa_txs, '2')]:
        if not txs:
            add_line(f"\n[{label}] 실거래 데이터가 존재하지 않습니다.")
            continue
            
        add_line(f"\n[{label} 시장 동향 (방수 추정별 세분화)]")
        
        groups = {
            "원룸형 (전용 20㎡ 미만)": [],
            "투룸형 (전용 20~40㎡)": [],
            "쓰리룸형 (전용 40~60㎡)": [],
            "대형 (전용 60㎡ 이상)": [],
            "지하층 (반지하 전체)": []
        }
        for t in txs:
            try:
                if is_basement_transaction(t):
                    groups["지하층 (반지하 전체)"].append(t)
                    continue
                area = float(t.get('excluUseAr', t.get('totalFloorAr', 0)))
                if area > 0:
                    grp_name = get_villa_group(area)
                    groups[grp_name].append(t)
            except:
                pass
                
        for grp_name in ["원룸형 (전용 20㎡ 미만)", "투룸형 (전용 20~40㎡)", "쓰리룸형 (전용 40~60㎡)", "대형 (전용 60㎡ 이상)", "지하층 (반지하 전체)"]:
            g_txs = groups[grp_name]
            g_trades = [t for t in g_txs if t.get('_trade_type') == '매매']
            g_jeonses = [t for t in g_txs if t.get('_trade_type') == '전세']
            g_wolses = [t for t in g_txs if t.get('_trade_type') == '월세']
            
            g_avg_trade = get_avg_price(g_trades)
            g_avg_jeonse = get_avg_price(g_jeonses)
            g_overall_rate = calculate_market_conversion_rate(g_txs)
            
            g_trade_str = local_format_price(g_avg_trade) if g_avg_trade else "-"
            if g_avg_jeonse:
                if g_avg_trade:
                    g_j_rate = int(round(g_avg_jeonse / g_avg_trade * 100))
                    g_jeonse_str = f"{local_format_price(g_avg_jeonse)} (전세가율 {g_j_rate}%)"
                else:
                    g_jeonse_str = local_format_price(g_avg_jeonse)
            else:
                g_jeonse_str = "-"
                
            g_rate_str = f"{g_overall_rate:.2f}%" if g_overall_rate else "-"
            
            add_line(f" • {grp_name}:")
            add_line(f"   - 거래 건수: 총 {len(g_txs)}건 (매매 {len(g_trades)} / 전세 {len(g_jeonses)} / 월세 {len(g_wolses)})")
            add_line(f"   - 평균 매매가: {g_trade_str} | 평균 전세금: {g_jeonse_str} | 전환율: {g_rate_str}")
            
        add_line(" ※ 안내: 위 방수(원룸/투룸 등) 분류는 실제 대장상 방수가 아닌, 실거래 전용면적 기준의 추정치입니다. 지하층(반지하)은 지상층 분류에서 제외 후 독립된 항목으로 분리 통계 처리되었습니다.")
            
        overall_rate = calculate_market_conversion_rate(txs)
        if overall_rate:
            seg_data = analyze_conversion_rate_segments(txs, prop_type)
            if seg_data:
                ths = seg_data['thresholds']
                add_line("\n • 보증금 구간별 전월세 전환율 상세 (전체 빌라 기준):")
                
                t0_str = local_format_price(ths[0]).replace(' ', '')
                t1_str = local_format_price(ths[1]).replace(' ', '')
                
                if seg_data['g1_rate']:
                    add_line(f"   - 소액 보증금 ({t0_str} 미만): {seg_data['g1_rate']:.2f}% ({seg_data['g1_count']}건)")
                if seg_data['g2_rate']:
                    add_line(f"   - 중소 보증금 ({t0_str} ~ {t1_str} 미만): {seg_data['g2_rate']:.2f}% ({seg_data['g2_count']}건)")
                if seg_data['g3_rate']:
                    add_line(f"   - 고액 보증금 ({t1_str} 이상): {seg_data['g3_rate']:.2f}% ({seg_data['g3_count']}건)")
                add_line(f"   ※ 안내: '보증금 구간'은 전환 금액이 아닌 월세 계약의 '최종 월세 보증금' 기준입니다. (예: 전세 4.5억 중 5천을 보증금으로 두고 전환 시 '중소 보증금' 구간 전환율 적용)")
        else:
            add_line("\n • 전월세 전환율: 분석을 위한 전세/월세 데이터 매칭 사례 부족")
            
        add_line("-" * 50)
        
    # Save Report files
    os.makedirs("reports", exist_ok=True)
    base_filename = f"reports/동향분석_{file_safe_dong}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    txt_filename = f"{base_filename}.txt"
    pdf_filename = f"{base_filename}.pdf"
    
    # Save TXT
    try:
        with open(txt_filename, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
        print(f"\n💾 텍스트 보고서 저장 완료: {os.path.abspath(txt_filename)}")
    except Exception as e:
        print(f"\n [!] 텍스트 보고서 저장 실패: {e}")
        
    # Generate & Save PDF
    try:
        member_info = load_member_info()
        generate_market_report_pdf(pdf_filename, display_dong_name, apt_txs, villa_txs, member_info, region_prefix=full_region_name, rep_apt_name=rep_apt_name, trend_data=trend_data, filtered_apt_txs=filtered_apt_txs)
        print(f"🎨 PDF 보고서 발행 완료 (중개사 서명 포함): {os.path.abspath(pdf_filename)}")
    except Exception as e:
        print(f" [!] PDF 보고서 생성 실패: {e}")
        
    input("\n메뉴로 돌아가려면 엔터를 누르세요...")

if __name__ == "__main__":
    run_market_analysis()
