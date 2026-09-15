import sys
import os
import re
import urllib.request
import urllib.parse
import json
import math
from datetime import datetime

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle

# Import utilities from trade_viewer
from trade_viewer import (
    get_kakao_address_info,
    get_recent_transactions,
    get_cached_admin_dong,
    normalize_h_dong_name,
    save_admin_dong_cache,
    load_admin_dong_cache
)

# Mapping of administrative dongs and minor legal dongs to legal dongs for combined analysis
DONG_GROUPS = {
    "성산1동": {
        "dongs": ["성산동"],
        "display": "성산1동 (성산동)"
    },
    "성산2동": {
        "dongs": ["성산동", "중동"],
        "display": "성산2동 (성산동, 중동)"
    },
    "중동": {
        "dongs": ["성산동", "중동"],
        "display": "성산2동 (성산동, 중동)"
    },
    "망원1동": {
        "dongs": ["망원동"],
        "display": "망원1동 (망원동)"
    },
    "망원2동": {
        "dongs": ["망원동"],
        "display": "망원2동 (망원동)"
    },
    "망원동": {
        "dongs": ["망원동"],
        "display": "망원동"
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
    },
    "용강동": {
        "dongs": ["용강동", "토정동", "마포동", "대흥동", "염리동"],
        "display": "용강동"
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
    else:
        return "쓰리룸 이상형 (전용 40㎡ 이상)"


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


# Note: Admin dong cache and helper functions are imported from trade_viewer


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

def find_office_map_file(dong_name=""):
    """
    사무소 약도(지도) 이미지 파일을 다양한 경로에서 탐색하여 절대 경로를 반환합니다.
    - 동별 맞춤 약도(seongsan_map 등) 또는 대표 사무소 약도(office_map, map, 약도 등) 지원
    """
    candidates = []
    
    # 1. 동 이름 기반 (성산동, 중동 등)
    if dong_name:
        clean_d = re.sub(r'[^가-힣a-zA-Z0-9]', '', str(dong_name))
        if any(x in clean_d for x in ["성산", "중동"]):
            candidates.extend(["seongsan_map", "seongsan_map_final_A", "seongsan_map_cleaned_A"])
        candidates.append(f"{clean_d}_map")
        
    # 2. 범용 사무소 약도 파일명
    candidates.extend([
        "office_map",
        "seongsan_map",
        "map",
        "약도",
        "사무실약도",
        "사무소약도"
    ])
    
    # 탐색할 디렉터리 목록
    base_dirs = []
    
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
    base_dirs.extend([
        os.path.join(base_dir, "assets"),
        os.path.join(base_dir, "..", "assets"),
        os.path.join(base_dir, "scratch"),
        base_dir
    ])
    
    if hasattr(sys, '_MEIPASS'):
        base_dirs.extend([
            os.path.join(sys._MEIPASS, "assets"),
            sys._MEIPASS
        ])
        
    base_dirs.extend([
        os.path.abspath("assets"),
        os.path.abspath("../assets"),
        os.path.abspath("."),
        os.path.abspath(".."),
        r"d:\부동산업무\antigravity\assets",
        r"d:\부동산업무\antigravity\AutoBot_Clean\assets",
        r"d:\부동산업무\antigravity\consult_diary\assets"
    ])
    
    extensions = [".png", ".jpg", ".jpeg", ".webp"]
    
    seen = set()
    for d in base_dirs:
        if not d:
            continue
        norm_d = os.path.normcase(os.path.abspath(d))
        if norm_d in seen or not os.path.exists(norm_d):
            continue
        seen.add(norm_d)
        for c in candidates:
            for ext in extensions:
                p = os.path.join(norm_d, c + ext)
                if os.path.isfile(p):
                    return os.path.abspath(p)
                    
    return None

def load_serve_listings_cache():
    """부동산써브 캐시 파일(serve_listings_cache.json)에서 매물 목록을 불러옵니다."""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    cache_path = os.path.join(base_dir, "serve_listings_cache.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                listings = json.load(f)
                if isinstance(listings, list):
                    return listings
        except Exception as e:
            pass
    return []

def check_and_refresh_serve_listings():
    """
    공인중개사법 준수: 보고서 생성 시 허위매물/거래완료 매물이 추천되지 않도록
    부동산써브 현재 등록 매물 관리 화면을 점검(스캔)하여 로컬 캐시를 최신화합니다.
    """
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    cache_path = os.path.join(base_dir, "serve_listings_cache.json")
    
    last_modified_str = "없음"
    if os.path.exists(cache_path):
        mtime = os.path.getmtime(cache_path)
        last_modified_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
        
    print("\n" + "=" * 60)
    print(" 🛡️  [공인중개사법 준수] 추천 매물 실시간 유효성 점검 (방법 B)")
    print("  ※ 거래완료/종료/비공개 매물의 추천 노출(표시·광고 위반)을 방지하기 위해")
    print("     현재 등록 중인 부동산써브 매물 목록을 점검합니다.")
    print(f"  - 마지막 매물 캐시 갱신일시: {last_modified_str}")
    print("=" * 60)
    print(" [1] 엔터(Enter)      : 크롬 브라우저에서 최신 매물 목록 스캔 & 갱신 (권장)")
    print(" [2] 's' 입력 후 엔터 : 기존 저장된 매물 캐시 파일 그대로 사용")
    print(" [3] 'n' 입력 후 엔터 : 이번 보고서에서 추천 매물 섹션 제외")
    
    choice = input(" 선택해 주세요 [기본값: 엔터(1번)]: ").strip().lower()
    
    if choice == 'n':
        print(" -> 추천 매물 섹션을 제외하고 보고서를 생성합니다.")
        return "skip"
    elif choice == 's':
        print(f" -> 기존 캐시({last_modified_str})를 사용합니다. (거래완료 매물 포함 가능성에 유의하세요)")
        return "cache"
        
    # [1] 스캔 진행
    print("\n -> 부동산써브 매물 관리 페이지를 확인합니다...")
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        import serve_auto_upload
    except Exception as e:
        print(f" [!] Selenium 또는 관련 모듈 로드 실패: {e}. 기존 캐시를 사용합니다.")
        return "cache"
        
    driver = None
    if getattr(serve_auto_upload, '_kept_alive_driver', None) is not None:
        try:
            _ = serve_auto_upload._kept_alive_driver.current_url
            driver = serve_auto_upload._kept_alive_driver
            print(" -> 기존에 열려 있는 부동산써브 크롬 브라우저를 재사용합니다.")
        except Exception:
            serve_auto_upload._kept_alive_driver = None
            
    if driver is None:
        try:
            options = Options()
            options.add_experimental_option("detach", True)
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("useAutomationExtension", False)
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            driver = webdriver.Chrome(options=options)
            serve_auto_upload._kept_alive_driver = driver
        except Exception as e:
            print(f" [!] 크롬 브라우저 실행 실패: {e}. 기존 캐시를 사용합니다.")
            return "cache"
            
    target_url = "https://ma.serve.co.kr/good/articleRegistList"
    try:
        if target_url not in driver.current_url:
            driver.get(target_url)
    except Exception:
        try:
            driver.get(target_url)
        except Exception as e:
            print(f" [!] 페이지 이동 실패: {e}. 기존 캐시를 사용합니다.")
            return "cache"
            
    print("\n[안내] 크롬 브라우저에서 부동산써브 로그인 후")
    print("       '통합매물관리' 목록 화면이 보이도록 준비해 주세요.")
    print("       (팁: 하단의 '페이지당 보기'를 50개/100개로 넓히시면 더 많은 매물이 스캔됩니다.)")
    user_confirm = input(" 매물 목록 화면이 열렸으면 엔터(Enter)를 치세요 (취소: 'c'): ").strip().lower()
    if user_confirm == 'c':
        print(" -> 스캔을 취소하고 기존 캐시를 사용합니다.")
        return "cache"
        
    print(" -> 현재 화면의 등록 매물을 정밀 스캔 중입니다...")
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "tr")
        listings = []
        for row in rows:
            try:
                text = row.text.strip()
                if not text:
                    continue
                serve_match = re.search(r'\b(33\d{7,8})\b', text)
                if not serve_match:
                    continue
                serve_id = serve_match.group(1)
                
                trade_type = "월세"
                price_str = ""
                price_wolse_match = re.search(r'월세\s*([0-9,]+)\s*/\s*([0-9,]+)', text)
                price_jeonse_match = re.search(r'전세\s*([0-9,]+)', text)
                price_trade_match = re.search(r'매매\s*([0-9,]+)', text)
                
                if price_wolse_match:
                    trade_type = "월세"
                    price_str = f"{price_wolse_match.group(1)} / {price_wolse_match.group(2)}"
                elif price_jeonse_match:
                    trade_type = "전세"
                    price_str = price_jeonse_match.group(1)
                elif price_trade_match:
                    trade_type = "매매"
                    price_str = price_trade_match.group(1)
                
                prop_type = "주택"
                type_match = re.search(r'(주택|아파트|오피스텔|상가|원룸|상가점포|빌라|연립|다세대)', text)
                if type_match:
                    prop_type = type_match.group(1)
                
                addr_match = re.search(r'([가-힣]+(?:시|도)\s+[가-힣]+(?:시|군|구)\s+[가-힣]+동)', text)
                if not addr_match:
                    addr_match = re.search(r'(서울특별시\s+[가-힣]+구\s+[가-힣]+동)', text)
                address = ""
                if addr_match:
                    address = addr_match.group(1).strip()
                    lot_match = re.search(r'\(([0-9]+-[0-9]+)\)', text)
                    if lot_match:
                        address += " " + lot_match.group(1)
                    else:
                        lot_match2 = re.search(r'동\s+([0-9]+(?:-[0-9]+)?)', text)
                        if lot_match2:
                            address += " " + lot_match2.group(1)
                
                detailed_address = ""
                detailed_match = re.search(r'(\d+동\s+\d+호|\d+호)', text)
                if detailed_match:
                    detailed_address = detailed_match.group(1)
                
                floor_info = ""
                floor_match = re.search(r'(-?\d+층\s*/\s*\d+층)', text)
                if floor_match:
                    floor_info = floor_match.group(1)
                    
                area_info = ""
                area_match = re.search(r'([\d.]+(?:\s*/\s*[\d.]+)?\(㎡\))', text)
                if area_match:
                    area_info = area_match.group(1)
                else:
                    area_match2 = re.search(r'([\d.]+\s*/\s*[\d.]+\s*㎡)', text)
                    if area_match2:
                        area_info = area_match2.group(1)
                
                feature = ""
                feature_match = re.search(r'매물특징\s*:\s*(.*)', text)
                if feature_match:
                    feature = feature_match.group(1).split('·')[0].split('\n')[0].strip()
                    
                move_in = ""
                move_in_match = re.search(r'입주정보\s*:\s*(.*)', text)
                if move_in_match:
                    move_in = move_in_match.group(1).split('·')[0].split('\n')[0].strip()
                    move_in = re.sub(r'(계약서\s*작성|공동중개|등록|매물정보|복사).*$', '', move_in).strip()
                
                listings.append({
                    "serve_id": serve_id,
                    "prop_type": prop_type,
                    "address": address,
                    "detailed_address": detailed_address,
                    "floor_info": floor_info,
                    "area_info": area_info,
                    "trade_type": trade_type,
                    "price_str": price_str,
                    "feature": feature,
                    "move_in": move_in
                })
            except Exception:
                pass
                
        if listings:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(listings, f, ensure_ascii=False, indent=2)
            print(f" -> ✅ 성공! 최신 등록 매물 {len(listings)}건 스캔 및 캐시 갱신 완료.")
            print("     (이미 거래 완료되거나 종료/내려진 매물은 자동 제외되었습니다.)")
            return "refreshed"
        else:
            print(" [!] 화면에서 등록된 매물을 찾지 못했습니다. 매물 관리 목록 화면인지 확인해주세요.")
            fallback_choice = input(" 기존 캐시 파일을 사용하시겠습니까? (Y/n): ").strip().lower()
            if fallback_choice == 'n':
                return "skip"
            return "cache"
    except Exception as e:
        print(f" [!] 스캔 중 오류 발생: {e}. 기존 캐시를 사용합니다.")
        return "cache"

def extract_target_dongs(target_dong_name):
    """'성산2동 (성산동, 중동)' 등의 다양한 형태의 동네 명칭에서 실제 법정동/행정동 목록을 추출합니다."""
    target_dongs = set()
    # 1. 정규표현식으로 모든 '..동' 형태 추출
    raw_dongs = re.findall(r'([가-힣0-9]+동)', target_dong_name)
    for d in raw_dongs:
        target_dongs.add(d)
        clean_d = re.sub(r'\d+동', '동', d)
        target_dongs.add(clean_d)
        if d in DONG_GROUPS:
            target_dongs.update(DONG_GROUPS[d].get('dongs', []))
        if clean_d in DONG_GROUPS:
            target_dongs.update(DONG_GROUPS[clean_d].get('dongs', []))
            
    # 2. 구분자(괄호, 쉼표, 슬래시 등) 기준 분할
    for chunk in re.split(r'[\s(),/]+', target_dong_name):
        chunk = chunk.strip()
        if not chunk:
            continue
        if not chunk.endswith('동'):
            chunk_dong = chunk + '동'
        else:
            chunk_dong = chunk
        target_dongs.add(chunk_dong)
        clean_chunk = re.sub(r'\d+동', '동', chunk_dong)
        target_dongs.add(clean_chunk)
        if chunk_dong in DONG_GROUPS:
            target_dongs.update(DONG_GROUPS[chunk_dong].get('dongs', []))
        if clean_chunk in DONG_GROUPS:
            target_dongs.update(DONG_GROUPS[clean_chunk].get('dongs', []))
            
    return [d for d in target_dongs if len(d) >= 2]

def select_cma_recommended_listings(target_dong_name, filtered_villa_txs, max_picks=2):
    """
    부동산써브 매물 중 분석 대상 동네의 다세대/빌라를 대상으로
    최근 6개월 실거래 통계(CMA)와 비교하여 가장 가격 경쟁력이 뛰어난 매물 2~3개를 엄선합니다.
    """
    listings = load_serve_listings_cache()
    if not listings:
        return []
        
    # 1. 대상 동네 키워드 매핑 (예: 성산2동 (성산동, 중동) -> ['성산동', '중동', '성산2동'])
    target_dongs = extract_target_dongs(target_dong_name)
    if not target_dongs:
        target_dongs = [target_dong_name]
        
    # 2. 실거래가 벤치마크 통계 산출 (방수 그룹 & 거래 유형별)
    benchmarks = {
        "원룸형 (전용 20㎡ 미만)": {"매매": [], "전세": [], "월세": []},
        "투룸형 (전용 20~40㎡)": {"매매": [], "전세": [], "월세": []},
        "쓰리룸 이상형 (전용 40㎡ 이상)": {"매매": [], "전세": [], "월세": []}
    }
    
    for t in filtered_villa_txs:
        if is_basement_transaction(t):
            continue
        try:
            area = float(t.get('excluUseAr', t.get('totalFloorAr', 0)))
            if area <= 0:
                continue
            grp = get_villa_group(area)
            tt = t.get('_trade_type', '')
            val_str = str(t.get('dealAmount', '') or t.get('rowPrice', '') or t.get('deposit', '') or t.get('guaranteeAmt', '')).strip().replace(',', '')
            if val_str and tt in ["매매", "전세"]:
                benchmarks[grp][tt].append(float(val_str))
            elif tt == "월세":
                dep_str = str(t.get('deposit', '') or t.get('guaranteeAmt', '') or t.get('rowPrice', '')).strip().replace(',', '')
                rent_str = str(t.get('monthlyRent', '') or t.get('monthly', '')).strip().replace(',', '')
                if dep_str and rent_str:
                    benchmarks[grp]["월세"].append((float(dep_str), float(rent_str)))
        except:
            pass

    # 3. 매물 필터링 및 CMA 평가
    candidates = []
    for item in listings:
        addr = item.get("address", "")
        # 지역 일치 여부
        if not any(d in addr for d in target_dongs):
            continue
            
        prop_type = item.get("prop_type", "주택")
        # 다세대/빌라/주택 여부 (아파트, 상가, 오피스텔 등 제외)
        if any(ex in prop_type for ex in ["아파트", "상가", "오피스텔", "토지", "공장", "사무실"]):
            continue
            
        floor_info = item.get("floor_info", "")
        # 반지하/지하 제외 (지상층 우선)
        if "지하" in floor_info or "-1층" in floor_info:
            continue
            
        # 면적 파싱
        area_info = item.get("area_info", "")
        excl_area = None
        if "/" in area_info:
            try:
                excl_area = float(area_info.split("/")[1].replace("(㎡)", "").replace("㎡", "").strip())
            except:
                pass
        if not excl_area:
            try:
                m = re.search(r'([0-9.]+)', area_info)
                if m:
                    excl_area = float(m.group(1))
            except:
                pass
        if not excl_area:
            excl_area = 30.0 # fallback
            
        room_grp = get_villa_group(excl_area)
        trade_type = item.get("trade_type", "전세")
        price_str = str(item.get("price_str", "")).strip()
        
        cma_reason = ""
        cma_score = 0 # 높을수록 우수한 가성비
        price_display = ""
        
        if trade_type in ["매매", "전세"]:
            try:
                p_val = float(price_str.replace(',', '').replace(' ', ''))
            except:
                continue
                
            price_display = f"{trade_type} {local_format_price(p_val)}"
            bm_prices = benchmarks[room_grp][trade_type]
            
            if bm_prices:
                avg_p = sum(bm_prices) / len(bm_prices)
                min_p = min(bm_prices)
                max_p = max(bm_prices)
                diff = avg_p - p_val
                
                if diff >= 1000:
                    cma_score = diff
                    cma_reason = f"최근 6개월 동일 평형({room_grp.split()[0]}) 평균 실거래가({local_format_price(avg_p)}) 대비 약 {local_format_price(diff)} 저렴한 급매성 추천 매물"
                elif p_val <= min_p * 1.05:
                    cma_score = 1500
                    cma_reason = f"최근 6개월 동일 평형 실거래 최저가 수준({local_format_price(min_p)})에 형성된 가성비 우수 매물"
                else:
                    cma_score = 500
                    cma_reason = f"동일 평형 실거래 시세 형성선({local_format_price(min_p)}~{local_format_price(max_p)}) 내 합리적 가격 및 우수 입지"
            else:
                cma_score = 300
                cma_reason = f"해당 지역 {room_grp.split()[0]} 대비 양호한 관리상태 및 실입주/임대 적합 매물"
                
        elif trade_type == "월세":
            parts = price_str.split("/")
            if len(parts) == 2:
                try:
                    dep_val = float(parts[0].replace(',', '').strip())
                    rent_val = float(parts[1].replace(',', '').strip())
                    price_display = f"보증금 {local_format_price(dep_val)} / 월 {local_format_price(rent_val)}"
                    cma_score = 800
                    cma_reason = "동네 평균 전월세 전환율 대비 합리적인 월차임 조건 및 주거 편의성 우수"
                except:
                    continue
            else:
                continue
                
        candidates.append({
            "serve_id": item.get("serve_id", ""),
            "room_grp": room_grp,
            "prop_type": prop_type,
            "address": addr,
            "detailed_address": item.get("detailed_address", ""),
            "floor_info": floor_info,
            "excl_area": excl_area,
            "trade_type": trade_type,
            "price_display": price_display,
            "feature": item.get("feature", "올수리 상태 양호, 주차 및 대중교통 편리"),
            "move_in": item.get("move_in", "즉시입주 협의"),
            "cma_reason": cma_reason,
            "cma_score": cma_score
        })
        
    if not candidates:
        return []
        
    # 4. 다양성 보장하며 상위 max_picks 선별 (예: 투룸 1건, 쓰리룸/매매 1건 등)
    candidates.sort(key=lambda x: x["cma_score"], reverse=True)
    
    selected = []
    seen_types = set()
    
    for cand in candidates:
        key = (cand["room_grp"], cand["trade_type"])
        if key not in seen_types:
            selected.append(cand)
            seen_types.add(key)
            if len(selected) >= max_picks:
                break
                
    if len(selected) < max_picks:
        for cand in candidates:
            if cand not in selected:
                selected.append(cand)
                if len(selected) >= max_picks:
                    break
                    
    return selected

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

def create_group_scatter_plot_drawing(transactions, title="평형별 단지 비교 산포도", target_type="매매"):
    from collections import defaultdict
    points_by_apt = defaultdict(list)
    min_date = None
    max_date = None
    
    PALETTE = ['#EF4444', '#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#14B8A6', '#EC4899']
    
    for t in transactions:
        if t.get("_trade_type") != target_type:
            continue
            
        try:
            dy = t.get("dealYear")
            dm = t.get("dealMonth")
            dd = t.get("dealDay", 1)
            if dy is None or dm is None: continue
                
            dt = datetime(int(dy), int(dm), int(dd))
            
            if target_type == "매매":
                price_str = str(t.get("dealAmount", "0")).replace(",", "").strip()
            else:
                price_str = str(t.get("deposit", "0") or t.get("guaranteeAmt", "0")).replace(",", "").strip()
                
            price = int(price_str)
            if price <= 0: continue
            
            if not min_date or dt < min_date: min_date = dt
            if not max_date or dt > max_date: max_date = dt
            
            apt_name = (t.get('aptNm') or t.get('mhouseNm') or '알수없음').strip()
            points_by_apt[apt_name].append((dt, price))
        except Exception as e:
            pass
            
    all_prices = []
    for pts in points_by_apt.values():
        all_prices.extend([p for _, p in pts])
        
    if not all_prices:
        return None
        
    min_p = min(all_prices)
    max_p = max(all_prices)
    diff = max_p - min_p
    if diff == 0: diff = 10000
    min_p = max(0, min_p - diff * 0.1)
    max_p = max_p + diff * 0.25
    
    dw = 515
    dh = 200
    d = Drawing(dw, dh)
    
    d.add(Rect(0, 0, dw, dh, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=1, rx=5, ry=5))
    d.add(String(15, dh - 20, f"🎯 {title} [{target_type}]", fontName='KoreanFont', fontSize=9, fillColor=colors.HexColor('#0F172A'), textAnchor='start'))
    
    cx = 50
    cy = 30
    cw = dw - 70
    ch = dh - 60
    
    for i in range(5):
        y_val = cy + i * (ch / 4)
        price_val = min_p + i * ((max_p - min_p) / 4)
        d.add(Line(cx, y_val, cx + cw, y_val, strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=0.5))
        if price_val >= 10000:
            lbl = f"{price_val/10000:.1f}억"
        else:
            lbl = f"{int(price_val):,}만"
        d.add(String(cx - 5, y_val - 3, lbl, fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#718096'), textAnchor='end'))
        
    if min_date and max_date and min_date != max_date:
        total_days = (max_date - min_date).days
        if total_days == 0: total_days = 1
        
        apt_names = sorted(points_by_apt.keys())
        legend_x = dw - 15
        
        for i, name in enumerate(apt_names):
            color = PALETTE[i % len(PALETTE)]
            pts = points_by_apt[name]
            
            max_pt_price = -1
            max_pt_dt = None
            
            for dt, p in pts:
                if p > max_pt_price:
                    max_pt_price = p
                    max_pt_dt = dt
                    
                x = cx + ((dt - min_date).days / total_days) * cw
                y = cy + ((p - min_p) / (max_p - min_p)) * ch
                
                if target_type == "전세":
                    d.add(Rect(x-2.5, y-2.5, 5, 5, fillColor=colors.HexColor(color), strokeColor=colors.HexColor('#ffffff'), strokeWidth=0.5))
                else:
                    d.add(Circle(x, y, 3, fillColor=colors.HexColor(color), strokeColor=colors.HexColor('#ffffff'), strokeWidth=0.5))
                    
            N = len(pts)
            if N > 1:
                sum_x = sum((dt - min_date).days for dt, p in pts)
                sum_y = sum(p for dt, p in pts)
                sum_x2 = sum(((dt - min_date).days)**2 for dt, p in pts)
                sum_xy = sum(((dt - min_date).days) * p for dt, p in pts)
                denom = (N * sum_x2 - sum_x**2)
                if denom != 0:
                    m = (N * sum_xy - sum_x * sum_y) / denom
                    c = (sum_y - m * sum_x) / N
                    y1_val = c
                    y2_val = m * total_days + c
                    plot_y1 = cy + ((y1_val - min_p) / (max_p - min_p)) * ch
                    plot_y2 = cy + ((y2_val - min_p) / (max_p - min_p)) * ch
                    
                    # Clip to plot area roughly if needed, but reportlab Line can go outside if we don't clip precisely.
                    # Simple clipping:
                    if plot_y1 < cy and plot_y2 > cy:
                        x_cross = cx + cw * ((cy - plot_y1) / (plot_y2 - plot_y1))
                        plot_y1 = cy
                        cx_start = x_cross
                    else:
                        cx_start = cx
                        
                    if plot_y1 > cy + ch and plot_y2 < cy + ch:
                        x_cross = cx + cw * ((plot_y1 - (cy + ch)) / (plot_y1 - plot_y2))
                        plot_y1 = cy + ch
                        cx_start = x_cross
                        
                    if plot_y2 < cy and plot_y1 > cy:
                        x_cross = cx + cw * ((plot_y1 - cy) / (plot_y1 - plot_y2))
                        plot_y2 = cy
                        cw_end = x_cross
                    else:
                        cw_end = cx + cw
                        
                    if plot_y2 > cy + ch and plot_y1 < cy + ch:
                        x_cross = cx + cw * (((cy + ch) - plot_y1) / (plot_y2 - plot_y1))
                        plot_y2 = cy + ch
                        cw_end = x_cross
                        
                    plot_y1 = max(cy, min(cy + ch, plot_y1))
                    plot_y2 = max(cy, min(cy + ch, plot_y2))
                    
                    d.add(Line(cx_start, plot_y1, cw_end, plot_y2, strokeColor=colors.HexColor(color), strokeWidth=1.2, strokeDashArray=[3, 3]))

            if max_pt_dt:
                x = cx + ((max_pt_dt - min_date).days / total_days) * cw
                y = cy + ((max_pt_price - min_p) / (max_p - min_p)) * ch
                lbl = f"최고 {max_pt_price/10000:.1f}억" if max_pt_price >= 10000 else f"최고 {max_pt_price:,}만"
                d.add(String(x, y + 5, lbl, fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor(color), textAnchor='middle'))
                
            str_w = len(name) * 8 + 15
            legend_x -= str_w
            d.add(Circle(legend_x + 5, dh - 17, 3, fillColor=colors.HexColor(color), strokeColor=None))
            d.add(String(legend_x + 12, dh - 20, name, fontName='KoreanFont', fontSize=8, fillColor=colors.HexColor('#475569')))
            
        d.add(String(cx, cy - 15, min_date.strftime("%Y.%m.%d"), fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#718096'), textAnchor='middle'))
        d.add(String(cx + cw, cy - 15, max_date.strftime("%Y.%m.%d"), fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#718096'), textAnchor='middle'))
        
        curr_y, curr_m = min_date.year, min_date.month
        curr_m += 1
        if curr_m > 12: curr_m = 1; curr_y += 1
        curr_dt = datetime(curr_y, curr_m, 1)
        while curr_dt < max_date:
            x_tick = cx + ((curr_dt - min_date).days / total_days) * cw
            d.add(Line(x_tick, cy, x_tick, cy - 3, strokeColor=colors.HexColor('#CBD5E1'), strokeWidth=0.5))
            d.add(Line(x_tick, cy, x_tick, cy + ch, strokeColor=colors.HexColor('#F1F5F9'), strokeWidth=0.5))
            total_months = (max_date.year - min_date.year) * 12 + max_date.month - min_date.month
            if total_months <= 12 or (curr_dt.month % 3 == 1):
                lbl = f"{str(curr_y)[2:]}.{str(curr_m).zfill(2)}"
                d.add(String(x_tick, cy - 10, lbl, fontName='KoreanFont', fontSize=6, fillColor=colors.HexColor('#94A3B8'), textAnchor='middle'))
            curr_m += 1
            if curr_m > 12: curr_m = 1; curr_y += 1
            curr_dt = datetime(curr_y, curr_m, 1)
        
    return d

def create_scatter_plot_drawing(transactions, title="실거래 산포도", draw_dots=True, target_bld_nm=None, dw=500, dh=155):
    trades = []
    jeonses = []
    min_date = None
    max_date = None
    
    clean_target_nm = ""
    if target_bld_nm:
        clean_target_nm = re.sub(r'\s*(?:제\s*)?[0-9A-Za-z가-힣]{1,4}\s*동\s*$', '', str(target_bld_nm)).strip().lower()

    for t in transactions:
        try:
            dy = t.get("dealYear")
            dm = t.get("dealMonth")
            dd = t.get("dealDay", 1)
            
            if dy is None or dm is None:
                continue
                
            dt = datetime(int(dy), int(dm), int(dd))
            
            # Check price
            if t.get("_trade_type") == "매매":
                price_str = str(t.get("dealAmount", "0")).replace(",", "").strip()
            else:
                price_str = str(t.get("deposit", "0") or t.get("guaranteeAmt", "0")).replace(",", "").strip()
                
            price = int(price_str)
            if price <= 0: continue
            
            # Target property determination
            is_target = t.get("_is_target_property")
            if is_target is None:
                if clean_target_nm:
                    apt_raw = (t.get("aptNm") or t.get("mhouseNm") or "").strip().lower()
                    apt_clean = re.sub(r'\s*(?:제\s*)?[0-9A-Za-z가-힣]{1,4}\s*동\s*$', '', apt_raw).strip()
                    is_target = bool(clean_target_nm in apt_clean or apt_clean in clean_target_nm)
                else:
                    is_target = True
            else:
                is_target = bool(is_target)

            if not min_date or dt < min_date: min_date = dt
            if not max_date or dt > max_date: max_date = dt
            
            if t.get("_trade_type") == "매매":
                trades.append((dt, price, is_target))
            elif t.get("_trade_type") == "전세":
                jeonses.append((dt, price, is_target))
        except Exception as e:
            pass
                
    all_prices = [p for _, p, _ in trades + jeonses]
    if not all_prices:
        d = Drawing(515, 100)
        d.add(Rect(0, 0, 515, 100, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#E2E8F0')))
        d.add(String(257, 50, "산포도를 그릴 데이터가 없습니다.", textAnchor='middle', fontName='KoreanFont', fontSize=10, fillColor=colors.HexColor('#718096')))
        return d
        
    min_p = min(all_prices)
    max_p = max(all_prices)
    diff = max_p - min_p
    if diff == 0: diff = 10000
    min_p = max(0, min_p - diff * 0.1)
    max_p = max_p + diff * 0.1
    
    dw = dw
    dh = dh
    d = Drawing(dw, dh)
    
    d.add(Rect(0, 0, dw, dh, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=1, rx=5, ry=5))
    d.add(String(15, dh - 20, f"🎯 {title} (최근 거래)", fontName='KoreanFont', fontSize=9, fillColor=colors.HexColor('#0F172A'), textAnchor='start'))
    
    # Check if we have mixed targets (both target apartment and similar/other apartments)
    all_targets = [is_t for _, _, is_t in trades + jeonses]
    has_mixed = any(not is_t for is_t in all_targets) and any(is_t for is_t in all_targets)
    
    def draw_cross_marker(drawing_obj, x, y, size=4.0, color='#B91C1C', stroke_width=2.0):
        # White outline underlay for distinct visibility
        drawing_obj.add(Line(x - size - 0.8, y, x + size + 0.8, y, strokeColor=colors.HexColor('#FFFFFF'), strokeWidth=stroke_width + 1.8, strokeLineCap=1))
        drawing_obj.add(Line(x, y - size - 0.8, x, y + size + 0.8, strokeColor=colors.HexColor('#FFFFFF'), strokeWidth=stroke_width + 1.8, strokeLineCap=1))
        # Foreground cross lines
        drawing_obj.add(Line(x - size, y, x + size, y, strokeColor=colors.HexColor(color), strokeWidth=stroke_width, strokeLineCap=1))
        drawing_obj.add(Line(x, y - size, x, y + size, strokeColor=colors.HexColor(color), strokeWidth=stroke_width, strokeLineCap=1))
        # Center core dot
        drawing_obj.add(Circle(x, y, 1.2, fillColor=colors.HexColor(color), strokeColor=None))

    # Legends
    if has_mixed:
        # Layout 4 legend items: 매매(유사), 매매(대상), 전세(유사), 전세(대상)
        d.add(Circle(dw - 245, dh - 17, 2.5, fillColor=colors.HexColor('#EF4444'), strokeColor=colors.HexColor('#B91C1C'), strokeWidth=0.5))
        d.add(String(dw - 238, dh - 20, "매매(유사)", fontName='KoreanFont', fontSize=7.5, fillColor=colors.HexColor('#475569')))
        
        draw_cross_marker(d, dw - 180, dh - 17, size=3.5, color='#B91C1C', stroke_width=1.8)
        d.add(String(dw - 172, dh - 20, "매매(대상)", fontName='KoreanFont', fontSize=7.5, fillColor=colors.HexColor('#B91C1C')))
        
        d.add(Rect(dw - 115, dh - 20, 5, 5, fillColor=colors.HexColor('#3B82F6'), strokeColor=colors.HexColor('#1D4ED8'), strokeWidth=0.5))
        d.add(String(dw - 106, dh - 20, "전세(유사)", fontName='KoreanFont', fontSize=7.5, fillColor=colors.HexColor('#475569')))
        
        draw_cross_marker(d, dw - 50, dh - 17, size=3.5, color='#1D4ED8', stroke_width=1.8)
        d.add(String(dw - 42, dh - 20, "전세(대상)", fontName='KoreanFont', fontSize=7.5, fillColor=colors.HexColor('#1D4ED8')))
    else:
        d.add(Circle(dw - 100, dh - 17, 3, fillColor=colors.HexColor('#EF4444'), strokeColor=None))
        d.add(String(dw - 90, dh - 20, "매매", fontName='KoreanFont', fontSize=8, fillColor=colors.HexColor('#475569')))
        
        d.add(Rect(dw - 53, dh - 20, 6, 6, fillColor=colors.HexColor('#3B82F6'), strokeColor=None))
        d.add(String(dw - 40, dh - 20, "전세", fontName='KoreanFont', fontSize=8, fillColor=colors.HexColor('#475569')))
    
    cx = 50
    cy = 30
    cw = dw - 70
    ch = dh - 60
    
    for i in range(5):
        y_val = cy + i * (ch / 4)
        price_val = min_p + i * ((max_p - min_p) / 4)
        d.add(Line(cx, y_val, cx + cw, y_val, strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=0.5))
        if price_val >= 10000:
            lbl = f"{price_val/10000:.1f}억"
        else:
            lbl = f"{int(price_val):,}만"
        d.add(String(cx - 5, y_val - 3, lbl, fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#718096'), textAnchor='end'))
        
    if min_date and max_date and min_date != max_date:
        total_days = (max_date - min_date).days
        if total_days == 0: total_days = 1
        
        def draw_trend_line(data_points, line_color):
            if len(data_points) < 2: return
            N = len(data_points)
            sum_x = sum((dt - min_date).days for dt, p, _ in data_points)
            sum_y = sum(p for dt, p, _ in data_points)
            sum_x2 = sum(((dt - min_date).days)**2 for dt, p, _ in data_points)
            sum_xy = sum(((dt - min_date).days) * p for dt, p, _ in data_points)
            
            denom = (N * sum_x2 - sum_x**2)
            if denom == 0: return
            
            m = (N * sum_xy - sum_x * sum_y) / denom
            c = (sum_y - m * sum_x) / N
            
            min_x_days = min((dt - min_date).days for dt, p, _ in data_points)
            max_x_days = max((dt - min_date).days for dt, p, _ in data_points)
            
            p1 = m * min_x_days + c
            p2 = m * max_x_days + c
            
            x1 = cx + (min_x_days / total_days) * cw
            y1 = cy + ((p1 - min_p) / (max_p - min_p)) * ch
            
            x2 = cx + (max_x_days / total_days) * cw
            y2 = cy + ((p2 - min_p) / (max_p - min_p)) * ch
            
            d.add(Line(x1, y1, x2, y2, strokeColor=colors.HexColor(line_color), strokeWidth=1, strokeDashArray=[4, 3]))

        draw_trend_line(trades, '#B91C1C')
        draw_trend_line(jeonses, '#1D4ED8')

        if draw_dots:
            # 1. 유사 단지 점 먼저 그리기 (배경 레이어)
            for dt, p, is_t in trades:
                if not is_t:
                    x = cx + ((dt - min_date).days / total_days) * cw
                    y = cy + ((p - min_p) / (max_p - min_p)) * ch
                    d.add(Circle(x, y, 2.5, fillColor=colors.HexColor('#EF4444'), strokeColor=colors.HexColor('#B91C1C'), strokeWidth=0.5))
                    
            for dt, p, is_t in jeonses:
                if not is_t:
                    x = cx + ((dt - min_date).days / total_days) * cw
                    y = cy + ((p - min_p) / (max_p - min_p)) * ch
                    d.add(Rect(x - 2.5, y - 2.5, 5, 5, fillColor=colors.HexColor('#3B82F6'), strokeColor=colors.HexColor('#1D4ED8'), strokeWidth=0.5))
            
            # 2. 분석 대상 단지 점 그리기 (전경 레이어 - 십자 마킹 또는 기본 모드)
            for dt, p, is_t in trades:
                if is_t:
                    x = cx + ((dt - min_date).days / total_days) * cw
                    y = cy + ((p - min_p) / (max_p - min_p)) * ch
                    if has_mixed:
                        draw_cross_marker(d, x, y, size=4.2, color='#B91C1C', stroke_width=2.0)
                    else:
                        d.add(Circle(x, y, 2.5, fillColor=colors.HexColor('#EF4444'), strokeColor=colors.HexColor('#B91C1C'), strokeWidth=0.5))
                        
            for dt, p, is_t in jeonses:
                if is_t:
                    x = cx + ((dt - min_date).days / total_days) * cw
                    y = cy + ((p - min_p) / (max_p - min_p)) * ch
                    if has_mixed:
                        draw_cross_marker(d, x, y, size=4.2, color='#1D4ED8', stroke_width=2.0)
                    else:
                        d.add(Rect(x - 2.5, y - 2.5, 5, 5, fillColor=colors.HexColor('#3B82F6'), strokeColor=colors.HexColor('#1D4ED8'), strokeWidth=0.5))
            
        d.add(String(cx, cy - 15, min_date.strftime("%Y.%m.%d"), fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#718096'), textAnchor='middle'))
        d.add(String(cx + cw, cy - 15, max_date.strftime("%Y.%m.%d"), fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#718096'), textAnchor='middle'))
        
        curr_y, curr_m = min_date.year, min_date.month
        curr_m += 1
        if curr_m > 12: curr_m = 1; curr_y += 1
        curr_dt = datetime(curr_y, curr_m, 1)
        while curr_dt < max_date:
            x_tick = cx + ((curr_dt - min_date).days / total_days) * cw
            d.add(Line(x_tick, cy, x_tick, cy - 3, strokeColor=colors.HexColor('#CBD5E1'), strokeWidth=0.5))
            d.add(Line(x_tick, cy, x_tick, cy + ch, strokeColor=colors.HexColor('#F1F5F9'), strokeWidth=0.5))
            total_months = (max_date.year - min_date.year) * 12 + max_date.month - min_date.month
            if total_months <= 12 or (curr_dt.month % 3 == 1):
                lbl = f"{str(curr_y)[2:]}.{str(curr_m).zfill(2)}"
                d.add(String(x_tick, cy - 10, lbl, fontName='KoreanFont', fontSize=6, fillColor=colors.HexColor('#94A3B8'), textAnchor='middle'))
            curr_m += 1
            if curr_m > 12: curr_m = 1; curr_y += 1
            curr_dt = datetime(curr_y, curr_m, 1)
        
    return d

def create_jeonse_ratio_trend_drawing(transactions, title="📈 전세가율 추세 (추세선 기반)"):
    trades = []
    jeonses = []
    min_date = None
    max_date = None
    
    for t in transactions:
        try:
            dy, dm, dd = t.get("dealYear"), t.get("dealMonth"), t.get("dealDay", 1)
            if not dy or not dm: continue
            dt = datetime(int(dy), int(dm), int(dd))
            
            is_trade = t.get("_trade_type") == "매매"
            is_jeonse = t.get("_trade_type") == "전세"
            if not is_trade and not is_jeonse: continue
            
            p_str = str(t.get("dealAmount", "0") if is_trade else t.get("deposit", "0") or t.get("guaranteeAmt", "0")).replace(",", "").strip()
            price = int(p_str)
            if price <= 0: continue
            
            if not min_date or dt < min_date: min_date = dt
            if not max_date or dt > max_date: max_date = dt
            
            if is_trade: trades.append((dt, price))
            elif is_jeonse: jeonses.append((dt, price))
        except: pass
        
    if len(trades) < 2 or len(jeonses) < 2 or min_date == max_date:
        return None
        
    total_days = (max_date - min_date).days
    if total_days == 0: total_days = 1
    
    def get_trend_params(data_points):
        N = len(data_points)
        sum_x = sum((dt - min_date).days for dt, p in data_points)
        sum_y = sum(p for dt, p in data_points)
        sum_x2 = sum(((dt - min_date).days)**2 for dt, p in data_points)
        sum_xy = sum(((dt - min_date).days) * p for dt, p in data_points)
        denom = (N * sum_x2 - sum_x**2)
        if denom == 0: return None
        m = (N * sum_xy - sum_x * sum_y) / denom
        c = (sum_y - m * sum_x) / N
        return m, c

    trade_trend = get_trend_params(trades)
    jeonse_trend = get_trend_params(jeonses)
    if not trade_trend or not jeonse_trend: return None
    
    m_t, c_t = trade_trend
    m_j, c_j = jeonse_trend
    
    ratios = []
    for d_val in range(0, total_days + 1, max(1, total_days // 20)):
        t_price = m_t * d_val + c_t
        j_price = m_j * d_val + c_j
        if t_price > 0 and j_price > 0:
            ratios.append((d_val, (j_price / t_price) * 100))
            
    if not ratios: return None
    
    min_r = min(r for _, r in ratios)
    max_r = max(r for _, r in ratios)
    diff = max_r - min_r
    if diff == 0: diff = 10
    min_r = max(0, min_r - diff * 0.2)
    max_r = min(100, max_r + diff * 0.2)
    if max_r - min_r < 5: max_r = min_r + 5

    dw, dh = 515, 130
    d = Drawing(dw, dh)
    d.add(Rect(0, 0, dw, dh, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=1, rx=5, ry=5))
    d.add(String(15, dh - 18, title, fontName='KoreanFont', fontSize=9, fillColor=colors.HexColor('#0F172A'), textAnchor='start'))
    
    cx, cy = 50, 25
    cw, ch = dw - 70, dh - 60
    
    for i in range(4):
        y_val = cy + i * (ch / 3)
        r_val = min_r + i * ((max_r - min_r) / 3)
        d.add(Line(cx, y_val, cx + cw, y_val, strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=0.5))
        d.add(String(cx - 5, y_val - 3, f"{r_val:.1f}%", fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#718096'), textAnchor='end'))

    from reportlab.graphics.shapes import PolyLine
    points = []
    for days, ratio in ratios:
        x = cx + (days / total_days) * cw
        y = cy + ((ratio - min_r) / (max_r - min_r)) * ch
        points.extend([x, y])
        
    if len(points) >= 4:
        d.add(PolyLine(points, strokeColor=colors.HexColor('#8B5CF6'), strokeWidth=2))
        
    d.add(String(cx, cy - 12, min_date.strftime("%Y.%m"), fontName='KoreanFont', fontSize=6, fillColor=colors.HexColor('#718096'), textAnchor='middle'))
    d.add(String(cx + cw, cy - 12, max_date.strftime("%Y.%m"), fontName='KoreanFont', fontSize=6, fillColor=colors.HexColor('#718096'), textAnchor='middle'))

    return d


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

def fit_log_curve_points(pts):
    """
    (pyung, unit_price) 목록을 받아 로그 곡선 Y = a + b * ln(X) 계수 (a, b)를 반환합니다.
    대지지분이 커질수록 지분평단가가 완만하게 하락하는 정비사업 지분가 특성을 모델링합니다.
    """
    if len(pts) < 3:
        return None
    valid_pts = [(p['pyung'], p['unit_price']) for p in pts if p['pyung'] > 0 and p['unit_price'] > 0]
    if len(valid_pts) < 3:
        return None
    try:
        u_vals = [math.log(x) for x, y in valid_pts]
        y_vals = [y for x, y in valid_pts]
        n = len(u_vals)
        u_mean = sum(u_vals) / n
        y_mean = sum(y_vals) / n
        denom = sum((u - u_mean)**2 for u in u_vals)
        if denom == 0:
            return None
        b = sum((u - u_mean) * (y - y_mean) for u, y in zip(u_vals, y_vals)) / denom
        a = y_mean - b * u_mean
        return a, b
    except:
        return None

def calculate_villa_land_bracket_stats(villa_txs):
    """
    다세대/빌라 매매 거래 데이터를 대지지분 구간별(5평 미만, 5~8평, 8~12평, 12평 이상)로
    5년 이내 신축과 5년 초과 구축으로 세분화하여 비교 통계를 산출합니다.
    """
    curr_year = datetime.now().year
    valid = []
    
    for t in villa_txs:
        if t.get('_trade_type') != '매매':
            continue
        try:
            land = float(t.get('landAr', 0) or 0)
            deal = float(str(t.get('dealAmount', '0')).replace(',', '').strip())
            b_year = int(t.get('buildYear', 0) or 0)
            if land > 0 and deal > 0:
                pyung = land * 0.3025
                price_per_py = deal / pyung
                if 0.5 <= pyung <= 35 and 500 <= price_per_py <= 25000:
                    is_new = (b_year >= curr_year - 5)
                    valid.append({
                        'pyung': pyung,
                        'unit_price': price_per_py,
                        'deal': deal,
                        'year': b_year,
                        'is_new': is_new,
                        'name': str(t.get('mhouseNm') or t.get('aptNm') or '빌라').strip()
                    })
        except:
            pass
            
    if not valid:
        return None
        
    old_pts = [v for v in valid if not v['is_new']]
    new_pts = [v for v in valid if v['is_new']]
    
    old_avg = round(sum(v['unit_price'] for v in old_pts) / len(old_pts)) if old_pts else 0
    new_avg = round(sum(v['unit_price'] for v in new_pts) / len(new_pts)) if new_pts else 0
    gap = (new_avg - old_avg) if (old_avg and new_avg) else 0
    
    ranges = [
        (0.0, 5.0, "5평 미만 (초소형)"),
        (5.0, 8.0, "5~8평 (소형)"),
        (8.0, 12.0, "8~12평 (중형)"),
        (12.0, 100.0, "12평 이상 (대형)")
    ]
    
    brackets = []
    for r_min, r_max, label in ranges:
        o_sub = [v for v in old_pts if r_min <= v['pyung'] < r_max]
        n_sub = [v for v in new_pts if r_min <= v['pyung'] < r_max]
        
        o_cnt = len(o_sub)
        n_cnt = len(n_sub)
        
        o_unit_avg = round(sum(v['unit_price'] for v in o_sub) / o_cnt) if o_cnt > 0 else None
        n_unit_avg = round(sum(v['unit_price'] for v in n_sub) / n_cnt) if n_cnt > 0 else None
        
        o_deal_avg = round(sum(v['deal'] for v in o_sub) / o_cnt) if o_cnt > 0 else None
        n_deal_avg = round(sum(v['deal'] for v in n_sub) / n_cnt) if n_cnt > 0 else None
        
        o_str = f"{o_unit_avg:,}만/평" if o_unit_avg else "-"
        n_str = f"{n_unit_avg:,}만/평" if n_unit_avg else "-"
        
        if o_deal_avg:
            o_deal_str = f"{o_deal_avg/10000:.1f}억" if o_deal_avg >= 10000 else f"{o_deal_avg:,}만"
        else:
            o_deal_str = "-"
            
        if n_deal_avg:
            n_deal_str = f"{n_deal_avg/10000:.1f}억" if n_deal_avg >= 10000 else f"{n_deal_avg:,}만"
        else:
            n_deal_str = "-"
            
        if o_unit_avg and n_unit_avg:
            diff = n_unit_avg - o_unit_avg
            gap_str = f"+{diff:,}만/평" if diff >= 0 else f"{diff:,}만/평"
        else:
            gap_str = "-"
            
        brackets.append({
            'label': label,
            'old_cnt': o_cnt,
            'new_cnt': n_cnt,
            'old_avg': o_unit_avg,
            'new_avg': n_unit_avg,
            'old_str': o_str,
            'new_str': n_str,
            'old_deal_str': o_deal_str,
            'new_deal_str': n_deal_str,
            'gap_str': gap_str
        })
        
    return {
        'total_valid': len(valid),
        'old_count': len(old_pts),
        'new_count': len(new_pts),
        'old_avg': old_avg,
        'new_avg': new_avg,
        'gap': gap,
        'brackets': brackets,
        'valid_items': valid
    }

def create_villa_land_scatter_plot_drawing(villa_txs, title="개발지/모아타운 대지지분 평당가 분석"):
    """
    대지지분(평) vs 지분평단가(만원/평) 산점도 및
    5년 기준 신축/구축 듀얼 곡선 차트 Drawing 생성
    """
    stats = calculate_villa_land_bracket_stats(villa_txs)
    if not stats or stats['total_valid'] < 3:
        d = Drawing(515, 100)
        d.add(Rect(0, 0, 515, 100, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#E2E8F0'), rx=5, ry=5))
        d.add(String(257, 50, "대지지분 분석을 위한 유효 매매 데이터가 부족합니다.", textAnchor='middle', fontName='KoreanFont', fontSize=10, fillColor=colors.HexColor('#718096')))
        return d
        
    valid = stats['valid_items']
    old_pts = [v for v in valid if not v['is_new']]
    new_pts = [v for v in valid if v['is_new']]
    
    dw = 515
    dh = 180
    d = Drawing(dw, dh)
    
    # 배경 카드
    d.add(Rect(0, 0, dw, dh, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=1, rx=6, ry=6))
    
    # 차트 제목
    d.add(String(14, dh - 17, f"🎯 {title}", fontName='KoreanFont', fontSize=9, fillColor=colors.HexColor('#0F172A'), textAnchor='start'))
    
    # 상단 범례 (Legends)
    # 구축 점
    d.add(Circle(dw - 235, dh - 14, 2.5, fillColor=colors.HexColor('#3B82F6'), strokeColor=colors.HexColor('#1D4ED8'), strokeWidth=0.5))
    d.add(String(dw - 228, dh - 17, "구축(5년초과)", fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#475569')))
    # 구축 곡선
    d.add(Line(dw - 175, dh - 14, dw - 162, dh - 14, strokeColor=colors.HexColor('#2563EB'), strokeWidth=1.8))
    d.add(String(dw - 158, dh - 17, "구축적정선", fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#2563EB')))
    # 신축 점
    d.add(Circle(dw - 110, dh - 14, 2.5, fillColor=colors.HexColor('#F97316'), strokeColor=colors.HexColor('#C2410C'), strokeWidth=0.5))
    d.add(String(dw - 103, dh - 17, "신축(5년이내)", fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#475569')))
    # 신축 곡선
    d.add(Line(dw - 50, dh - 14, dw - 37, dh - 14, strokeColor=colors.HexColor('#EA580C'), strokeWidth=1.8))
    d.add(String(dw - 33, dh - 17, "신축선", fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#EA580C')))
    
    cx = 45
    cy = 28
    cw = dw - 65
    ch = dh - 54
    
    # 동적 스케일 설정
    max_pyung_data = max(p['pyung'] for p in valid)
    max_x = min(25.0, max(15.0, math.ceil(max_pyung_data / 5.0) * 5.0))
    min_x = 0.0
    
    max_price_data = max(p['unit_price'] for p in valid)
    max_y = min(14000.0, max(9000.0, math.ceil(max_price_data / 2000.0) * 2000.0))
    min_y = 0.0
    
    # Y축 눈금선 (지분평단가)
    y_steps = 5
    for i in range(y_steps + 1):
        y_frac = i / y_steps
        y_pos = cy + y_frac * ch
        y_val = min_y + y_frac * (max_y - min_y)
        d.add(Line(cx, y_pos, cx + cw, y_pos, strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=0.5))
        if y_val == 0:
            lbl = "0"
        elif y_val >= 10000:
            lbl = f"{y_val/10000:.1f}억"
        else:
            lbl = f"{int(y_val):,}만"
        d.add(String(cx - 5, y_pos - 3, lbl, fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#94A3B8'), textAnchor='end'))
        
    # X축 눈금선 (대지지분 평)
    x_steps = int(max_x / 5)
    for i in range(1, x_steps + 1):
        x_val = i * 5.0
        x_pos = cx + (x_val / max_x) * cw
        d.add(Line(x_pos, cy, x_pos, cy + ch, strokeColor=colors.HexColor('#F1F5F9'), strokeWidth=0.5))
        d.add(Line(x_pos, cy, x_pos, cy - 3, strokeColor=colors.HexColor('#CBD5E1'), strokeWidth=0.5))
        d.add(String(x_pos, cy - 12, f"{int(x_val)}평", fontName='KoreanFont', fontSize=7, fillColor=colors.HexColor('#94A3B8'), textAnchor='middle'))
        
    d.add(String(cx + cw, cy - 12, "(대지지분)", fontName='KoreanFont', fontSize=6.5, fillColor=colors.HexColor('#94A3B8'), textAnchor='end'))
    d.add(String(cx - 5, cy + ch + 3, "(단가/평)", fontName='KoreanFont', fontSize=6.5, fillColor=colors.HexColor('#94A3B8'), textAnchor='end'))
    
    # 듀얼 로그 추세 곡선 피팅 및 그리기
    old_fit = fit_log_curve_points(old_pts)
    new_fit = fit_log_curve_points(new_pts)
    
    # 1) 구축 적정선 (Blue solid line)
    if old_fit:
        a_old, b_old = old_fit
        curve_pts_old = []
        sample_steps = 30
        for s in range(sample_steps + 1):
            px = 1.5 + (max_x - 1.5) * (s / sample_steps)
            py = a_old + b_old * math.log(px)
            if min_y <= py <= max_y:
                cx_pos = cx + (px / max_x) * cw
                cy_pos = cy + ((py - min_y) / (max_y - min_y)) * ch
                curve_pts_old.append((cx_pos, cy_pos))
                
        for idx in range(len(curve_pts_old) - 1):
            x1, y1 = curve_pts_old[idx]
            x2, y2 = curve_pts_old[idx + 1]
            d.add(Line(x1, y1, x2, y2, strokeColor=colors.HexColor('#2563EB'), strokeWidth=1.8))
            
    # 2) 신축 프리미엄선 (Orange line)
    if new_fit and len(new_pts) >= 4:
        a_new, b_new = new_fit
        curve_pts_new = []
        max_new_x = min(max_x, max(p['pyung'] for p in new_pts) + 1.0)
        sample_steps = 25
        for s in range(sample_steps + 1):
            px = 1.5 + (max_new_x - 1.5) * (s / sample_steps)
            py = a_new + b_new * math.log(px)
            if min_y <= py <= max_y:
                cx_pos = cx + (px / max_x) * cw
                cy_pos = cy + ((py - min_y) / (max_y - min_y)) * ch
                curve_pts_new.append((cx_pos, cy_pos))
                
        for idx in range(len(curve_pts_new) - 1):
            x1, y1 = curve_pts_new[idx]
            x2, y2 = curve_pts_new[idx + 1]
            d.add(Line(x1, y1, x2, y2, strokeColor=colors.HexColor('#EA580C'), strokeWidth=1.8))
            
    # 데이터 점 플롯
    # 1. 구축 점들 (파란색)
    for p in old_pts:
        px = p['pyung']
        py = p['unit_price']
        if px > max_x: continue
        py_clipped = min(max_y, max(min_y, py))
        x_coord = cx + (px / max_x) * cw
        y_coord = cy + ((py_clipped - min_y) / (max_y - min_y)) * ch
        d.add(Circle(x_coord, y_coord, 2.2, fillColor=colors.HexColor('#3B82F6'), strokeColor=colors.HexColor('#1D4ED8'), strokeWidth=0.5))
        
    # 2. 신축 점들 (주황색)
    for p in new_pts:
        px = p['pyung']
        py = p['unit_price']
        if px > max_x: continue
        py_clipped = min(max_y, max(min_y, py))
        x_coord = cx + (px / max_x) * cw
        y_coord = cy + ((py_clipped - min_y) / (max_y - min_y)) * ch
        d.add(Circle(x_coord, y_coord, 2.8, fillColor=colors.HexColor('#F97316'), strokeColor=colors.HexColor('#C2410C'), strokeWidth=0.6))
        
    return d

def build_villa_land_stat_table(villa_txs, cell_style, header_style):
    """
    PDF 보고서용: 지분 구간별 5년 신축 vs 구축 비교 통계 테이블 생성
    """
    stats = calculate_villa_land_bracket_stats(villa_txs)
    if not stats or stats['total_valid'] < 3:
        return None
        
    table_data = [
        [
            Paragraph("<b>대지지분 구간</b>", header_style),
            Paragraph("<b>구축(5년초과) 평균</b>", header_style),
            Paragraph("<b>신축(5년이내) 평균</b>", header_style),
            Paragraph("<b>신축 프리미엄 격차</b>", header_style),
            Paragraph("<b>투자 가이드</b>", header_style),
        ]
    ]
    
    guides = {
        "5평 미만 (초소형)": "소액 갭투자 밀집 (지분단가 극상단)",
        "5~8평 (소형)": "모아타운 주력 (거래 가장 활발)",
        "8~12평 (중형)": "지분 대비 가성비 우수 (알짜 매물)",
        "12평 이상 (대형)": "순수 대지 지분 (신축 쪼개기 불가)"
    }
    
    for b in stats['brackets']:
        o_text = f"<b>{b['old_str']}</b><br/><font size=6.5 color='#64748B'>({b['old_cnt']}건 | 평균 {b['old_deal_str']})</font>" if b['old_cnt'] > 0 else "-"
        n_text = f"<b>{b['new_str']}</b><br/><font size=6.5 color='#64748B'>({b['new_cnt']}건 | 평균 {b['new_deal_str']})</font>" if b['new_cnt'] > 0 else "-"
        
        diff_color = "#EA580C" if "+" in b['gap_str'] else "#2563EB"
        gap_text = f"<font color='{diff_color}'><b>{b['gap_str']}</b></font>" if b['gap_str'] != "-" else "-"
        guide_text = guides.get(b['label'], "-")
        
        table_data.append([
            Paragraph(f"<b>{b['label']}</b>", cell_style),
            Paragraph(o_text, cell_style),
            Paragraph(n_text, cell_style),
            Paragraph(gap_text, cell_style),
            Paragraph(f"<font size=7 color='#475569'>{guide_text}</font>", cell_style),
        ])
        
    stat_table = Table(table_data, colWidths=[110, 105, 105, 95, 100])
    stat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEABOVE', (0,0), (-1,0), 1, colors.HexColor('#0F172A')),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#0F172A')),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('LINEBELOW', (0,-1), (-1,-1), 1, colors.HexColor('#0F172A')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    
    for idx in range(1, len(table_data)):
        bg_color = colors.HexColor('#FFFFFF') if idx % 2 == 1 else colors.HexColor('#F8FAFC')
        stat_table.setStyle(TableStyle([('BACKGROUND', (0, idx), (-1, idx), bg_color)]))
        
    return stat_table

def generate_market_report_pdf(pdf_filename, bjdong_nm, villa_txs, member_info=None, region_prefix="서울특별시 마포구", cma_picks=None):
    font_name = register_korean_font()
        
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
        bold=True,
        keepWithNext=True
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
    
    office_name = ""
    broker_name = ""
    formatted_phone = ""
    
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
        
        office_name = member_info.get("office_name") or member_info.get("office") or ""
        broker_name = member_info.get("name") or "대표"
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
                
        slogan_text = f"※ 본 보고서는 성공적인 부동산 투자를 위해 <b>{office_name}</b>에서 제공하는 VIP 자산 분석 리포트입니다." if office_name else "※ 본 보고서는 성공적인 부동산 투자를 위해 제공되는 VIP 자산 분석 리포트입니다."
        
        header_table_data = [[Paragraph(slogan_text, header_left_style)]]
        header_table = Table(header_table_data, colWidths=[515])
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
    if office_name:
        main_title = f"📊 [{office_name}] {bjdong_nm} 프리미엄 부동산 동향 리포트"
    else:
        main_title = f"📊 {region_prefix} {bjdong_nm} 부동산 동향 리포트"
    story.append(Paragraph(main_title, title_style))
    
    # Metadata Box
    phone_style = ParagraphStyle(
        'PhoneStyle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#B45309'),
        bold=True
    )
    
    if office_name:
        publisher_text = f"{office_name} (담당: {broker_name})"
    else:
        publisher_text = "전문 공인중개사사무소"

    meta_data = [
        [Paragraph("<b>발행 및 분석</b>", body_style), Paragraph(publisher_text, body_style)],
        [Paragraph("<b>상담 직통번호</b>", body_style), Paragraph(f"📞 {formatted_phone}", phone_style)],
        [Paragraph("<b>분석 대상 지역</b>", body_style), Paragraph(f"{region_prefix} {bjdong_nm} (최근 6~24개월 실거래 기준)", body_style)],
        [Paragraph("<b>보고서 발행일</b>", body_style), Paragraph(datetime.now().strftime("%Y년 %m월 %d일"), body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[100, 415])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#475569')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))
    
    def build_prop_section(label, txs, prop_type, full_txs=None):
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
        
        prop_name = label.split()[1] if len(label.split()) > 1 else "해당 부동산"
        chart_drawing = create_scatter_plot_drawing(txs, title=f"📈 {prop_name} 실거래 점분포 (매매/전세)")
        if chart_drawing:
            sect_story.append(chart_drawing)
            sect_story.append(Spacer(1, 10))
            
        ratio_drawing = create_jeonse_ratio_trend_drawing(txs, title=f"📊 {prop_name} 매매가 대비 전세가율 추세 (추세선 기반)")
        if ratio_drawing:
            sect_story.append(ratio_drawing)
            sect_story.append(Spacer(1, 10))
        
        def get_price_range(subset):
            prices = []
            for item in subset:
                val = str(item.get('dealAmount', '') or item.get('rowPrice', '') or item.get('deposit', '') or item.get('guaranteeAmt', '')).strip().replace(',', '')
                if val:
                    try:
                        prices.append(float(val))
                    except:
                        pass
            if not prices: return None
            min_p = min(prices)
            max_p = max(prices)
            if min_p == max_p:
                return local_format_price(min_p)
            return f"{local_format_price(min_p)} ~ {local_format_price(max_p)}"
            
        if prop_type == '2':
            # Villa specific grouped table
            groups = {
                "원룸형 (전용 20㎡ 미만)": [],
                "투룸형 (전용 20~40㎡)": [],
                "쓰리룸 이상형 (전용 40㎡ 이상)": [],
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
                    Paragraph("<b>매매가 (최저~최고)</b>", table_hdr_style), 
                    Paragraph("<b>전세금 (최저~최고)</b>", table_hdr_style), 
                    Paragraph("<b>평균 전환율</b>", table_hdr_style)
                ]
            ]
            
            main_groups = ["원룸형 (전용 20㎡ 미만)", "투룸형 (전용 20~40㎡)", "쓰리룸 이상형 (전용 40㎡ 이상)"]
            for grp_name in main_groups:
                g_txs = groups[grp_name]
                g_trades = [t for t in g_txs if t.get('_trade_type') == '매매']
                g_jeonses = [t for t in g_txs if t.get('_trade_type') == '전세']
                g_wolses = [t for t in g_txs if t.get('_trade_type') == '월세']
                
                g_trade_str = get_price_range(g_trades) or "-"
                g_jeonse_str = get_price_range(g_jeonses) or "-"
                
                g_overall_rate = calculate_market_conversion_rate(g_txs)
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
                
            sect_story.append(stat_table)
            
            # Basement specific table
            sect_story.append(Spacer(1, 15))
            sect_story.append(Paragraph("■ [참고] 지하층(반지하) 시장 분석 동향", h2_style))
            
            b_txs = groups["지하층 (반지하 전체)"]
            b_trades = [t for t in b_txs if t.get('_trade_type') == '매매']
            b_jeonses = [t for t in b_txs if t.get('_trade_type') == '전세']
            b_wolses = [t for t in b_txs if t.get('_trade_type') == '월세']
            
            b_trade_str = get_price_range(b_trades) or "-"
            b_jeonse_str = get_price_range(b_jeonses) or "-"
            b_overall_rate = calculate_market_conversion_rate(b_txs)
            b_rate_str = f"{b_overall_rate:.2f}%" if b_overall_rate else "-"
            
            b_count_p = Paragraph(
                f"총 {len(b_txs)}건<br/><font size=6.5 color='#718096'>(매{len(b_trades)}/전{len(b_jeonses)}/월{len(b_wolses)})</font>", 
                table_cell_center
            )
            
            b_stat_data = [
                [
                    Paragraph("<b>구분 (특수매물)</b>", table_hdr_style), 
                    Paragraph("<b>총 거래 건수</b>", table_hdr_style), 
                    Paragraph("<b>매매가 (최저~최고)</b>", table_hdr_style), 
                    Paragraph("<b>전세금 (최저~최고)</b>", table_hdr_style), 
                    Paragraph("<b>평균 전환율</b>", table_hdr_style)
                ],
                [
                    Paragraph("지하층 (반지하 전체)", table_cell_center),
                    b_count_p,
                    Paragraph(b_trade_str, table_cell_center),
                    Paragraph(b_jeonse_str, table_cell_center),
                    Paragraph(b_rate_str, table_cell_center)
                ]
            ]
            
            b_stat_table = Table(b_stat_data, colWidths=[140, 95, 90, 100, 90])
            b_stat_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#475569')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LINEABOVE', (0,0), (-1,0), 1, colors.HexColor('#334155')),
                ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#334155')),
                ('LINEBELOW', (0,1), (-1,-1), 1, colors.HexColor('#334155')),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#FDFBF7'))
            ]))
            sect_story.append(b_stat_table)
            
            # Explanation for basement
            b_expl_style = ParagraphStyle(
                'BasementExpl',
                parent=styles['Normal'],
                fontName=font_name,
                fontSize=7.5,
                leading=11,
                textColor=colors.HexColor('#B45309')
            )
            sect_story.append(Spacer(1, 4))
            sect_story.append(Paragraph("※ 지하층(반지하)은 전세보증금 규모가 작아 전월세 전환율이 지상층 대비 높게 산출되는 특징이 있으나, 환금성 및 채광/습기 등 특수성을 고려해야 합니다.", b_expl_style))

            # --- 모아타운·개발지 대지지분 평당가 분석 차트 및 5년 신축/구축 듀얼 곡선 ---
            target_land_txs = full_txs if full_txs else txs
            land_chart = create_villa_land_scatter_plot_drawing(target_land_txs, title="개발지/모아타운 대지지분 평당가 산점도")
            if land_chart:
                land_block = [
                    Spacer(1, 12),
                    Paragraph("■ 🎯 [개발지/모아타운 핵심 지표] 대지지분 평당가 분석 및 5년 신축/구축 듀얼 곡선", h2_style),
                    Spacer(1, 4),
                    land_chart,
                    Spacer(1, 6)
                ]
                land_table = build_villa_land_stat_table(target_land_txs, table_cell_center, table_hdr_style)
                if land_table:
                    land_block.append(land_table)
                    land_block.append(Spacer(1, 6))
                sect_story.append(KeepTogether(land_block))

        else:
            # Apartment specific table
            trade_str = get_price_range(trades) or "거래 사례 없음"
            jeonse_str = get_price_range(jeonses) or "거래 사례 없음"
                
            rate_str = f"{overall_rate:.2f}%" if overall_rate else "산출 불가"
            
            stat_data = [
                [Paragraph("<b>구분</b>", table_hdr_style), Paragraph("<b>총 거래 건수</b>", table_hdr_style), Paragraph("<b>매매가 (최저~최고)</b>", table_hdr_style), Paragraph("<b>전세금 (최저~최고)</b>", table_hdr_style), Paragraph("<b>평균 전월세전환율</b>", table_hdr_style)],
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
        
    pass
            
    # Add Villa sections
    story.extend(build_prop_section("🏡 연립/다세대/빌라 (지상층·최근 6개월 기준)", filtered_villa_txs, '2', full_txs=villa_txs))
    
    # [CMA 정밀 시세 분석 기반] 이달의 추천 매물 (Best Value Pick)
    if cma_picks is None:
        cma_picks = select_cma_recommended_listings(bjdong_nm, filtered_villa_txs, max_picks=2)
    if cma_picks:
        rec_title_style = ParagraphStyle(
            'RecTitle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor('#0F172A'),
            bold=True,
            spaceBefore=14,
            spaceAfter=3,
            keepWithNext=True
        )
        rec_sub_style = ParagraphStyle(
            'RecSub',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=7.5,
            leading=11,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=6,
            keepWithNext=True
        )
        card_header_left = ParagraphStyle(
            'CardHdrLeft',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor('#0F172A'),
            bold=True
        )
        card_header_right = ParagraphStyle(
            'CardHdrRight',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#0284C7'),
            alignment=2, # Right
            bold=True
        )
        card_cma_style = ParagraphStyle(
            'CardCMA',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=7.5,
            leading=11,
            textColor=colors.HexColor('#1E40AF')
        )
        card_feat_style = ParagraphStyle(
            'CardFeat',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=7.5,
            leading=11,
            textColor=colors.HexColor('#475569')
        )
        
        story.append(Spacer(1, 10))
        story.append(Paragraph("■ [CMA 기반 엄선] 이달의 추천 매물 (Best Value Pick)", rec_title_style))
        story.append(Paragraph("※ 최근 6개월 국토교통부 실거래 데이터 대비 가격 경쟁력 및 거주/투자가치(CMA)가 검증된 추천 매물입니다.", rec_sub_style))
        
        for idx, p in enumerate(cma_picks, 1):
            short_addr = p['address'].replace("서울특별시 ", "").replace("서울시 ", "")
            flr_disp = p['floor_info'].split('/')[0].strip() if '/' in p['floor_info'] else p['floor_info']
            if not flr_disp: flr_disp = "지상층"
            
            card_data = [
                [
                    Paragraph(f"<b><font color='#0284C7'>[추천 {idx}]</font> {p['prop_type']} ({short_addr})</b> <font size=7.5 color='#64748B'>| 전용 {p['excl_area']:.1f}㎡ / {flr_disp}</font>", card_header_left),
                    Paragraph(f"<b>{p['price_display']}</b>", card_header_right)
                ],
                [
                    Paragraph(f"<b>📊 CMA 분석 근거:</b> {p['cma_reason']}", card_cma_style),
                    ""
                ],
                [
                    Paragraph(f"<b>📌 매물 특징:</b> {p['feature']}" + (f" <font color='#64748B'>(입주: {p['move_in']})</font>" if p.get('move_in') else ""), card_feat_style),
                    ""
                ]
            ]
            card_table = Table(card_data, colWidths=[385, 130])
            card_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFFFF')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
                ('SPAN', (0,1), (1,1)),
                ('SPAN', (0,2), (1,2)),
                ('BACKGROUND', (0,1), (1,1), colors.HexColor('#EFF6FF')),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ('LINEBELOW', (0,0), (-1,0), 0.5, colors.HexColor('#E2E8F0')),
                ('LINEBELOW', (0,1), (-1,1), 0.5, colors.HexColor('#DBEAFE')),
            ]))
            story.append(card_table)
            story.append(Spacer(1, 5))
            
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
            spaceAfter=5,
            keepWithNext=True
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
            spaceAfter=5,
            keepWithNext=True
        )
        
        # Add analyst job title to broker name
        broker_name = member_info.get('name', '')
        if broker_name == "조항준 공인중개사":
            formatted_broker_name = "공인중개사 조항준"
        else:
            formatted_broker_name = broker_name if broker_name else "-"
        
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
                Paragraph("<b>대표</b>", body_style),
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
        
    # Office Map Section (찾아오시는 길 / 사무소 약도)
    map_img_path = find_office_map_file(bjdong_nm)
    if map_img_path and os.path.exists(map_img_path):
        map_title_style = ParagraphStyle(
            'MapTitle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor('#1E293B'),
            bold=True,
            spaceBefore=6,
            spaceAfter=2,
            keepWithNext=True
        )
        map_sub_style = ParagraphStyle(
            'MapSub',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=4,
            keepWithNext=True
        )
        
        office_nm = ""
        addr_str = ""
        if member_info:
            office_nm = member_info.get("office_name") or member_info.get("office") or ""
            addr_str = member_info.get("office_address", "")
        if not office_nm:
            office_nm = "신대림공인중개사사무소"
        if not addr_str:
            addr_str = "서울 마포구 모래내로 7길 52"
            
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"■ 찾아오시는 길 ({office_nm} 약도)", map_title_style))
        story.append(Paragraph(f"📍 {addr_str} (중동초등학교 인근 / 성산2동주민센터 도보 3분)", map_sub_style))
        
        try:
            from PIL import Image as PILImage
            with PILImage.open(map_img_path) as im:
                orig_w, orig_h = im.size
            aspect = orig_w / float(orig_h) if orig_h > 0 else 1.5538
        except Exception:
            aspect = 1.5538
            
        # Target sizing that fits gracefully within Page 3
        map_w = 460
        map_h = int(map_w / aspect)
        if map_h > 240:
            map_h = 240
            map_w = int(map_h * aspect)
            
        map_img = Image(map_img_path, width=map_w, height=map_h)
        map_card = Table([[map_img]], colWidths=[515])
        map_card.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFFFF')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 3),
            ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(map_card)

    # Disclaimer Box
    story.append(Spacer(1, 8))
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

def clean_and_extract_dong(user_input):
    raw = user_input.strip()
    words = raw.split()
    if words:
        last = words[-1]
        if not any(last.endswith(s) for s in ['동', '가', '리', '로', '길']):
            words[-1] = last + '동'
        raw = ' '.join(words)
    pure = raw
    while True:
        m = re.match(r'^(?:서울(?:특별)?시|서울|경기(?:도)?|인천(?:광역시)?|부산(?:광역시)?|대구(?:광역시)?|대전(?:광역시)?|광주(?:광역시)?|울산(?:광역시)?|세종(?:특별자치시)?|[가-힣]{2,}(?:시|도|구|군))\s*(.*)$', pure)
        if m and m.group(1):
            pure = m.group(1).strip()
        else:
            break
    return raw, pure

def run_market_analysis():
    print("==================================================")
    print("      동네별 부동산 시장 동향 및 전월세 분석      ")
    print("==================================================")
    
    dong_input = input("분석할 동 이름을 입력하세요 (예: 성산동, 수색동, 망원동): ").strip()
    if not dong_input:
        return
        
    raw_dong, pure_dong = clean_and_extract_dong(dong_input)
        
    # Determine default region prefix from member_info if available
    member_info = load_member_info()
    default_prefix = "서울특별시 마포구"
    if member_info and member_info.get("office_address"):
        addr_parts = member_info["office_address"].split()
        if len(addr_parts) >= 2:
            default_prefix = f"{addr_parts[0]} {addr_parts[1]}"
            
    # Check if the input already contains regional terms
    has_region = any(word.endswith(('시', '도', '구', '군')) for word in raw_dong.split()[:-1])
    if has_region:
        search_query = raw_dong
    else:
        search_query = f"{default_prefix} {pure_dong}"
        
    print(f"\n -> 주소 확인 및 코드 조회 중: {search_query}...")
    addr_info = get_kakao_address_info(search_query)
    
    # Fallback with numeric stripping if initial search fails or if bjdongNm is empty (e.g. administrative dong query)
    if not addr_info or not addr_info.get('bjdongNm'):
        fallback_dong = re.sub(r'\s*\d+\s*동$', '동', pure_dong)
        search_query_fb = fallback_dong if has_region else f"{default_prefix} {fallback_dong}"
        fb_info = get_kakao_address_info(search_query_fb)
        if fb_info:
            if not addr_info:
                addr_info = fb_info
            else:
                if not addr_info.get('bjdongNm'):
                    addr_info['bjdongNm'] = fb_info.get('bjdongNm', '')
        
    if not addr_info or not addr_info.get('sigunguCd'):
        print(" [!] 주소 변환 실패! 올바른 동 이름을 입력해주세요.")
        return
        
    bjdong_nm = addr_info.get('bjdongNm', '')
    sigunguCd = addr_info['sigunguCd']
    sido_nm = addr_info.get('sidoNm', '')
    sigungu_nm = addr_info.get('sigunguNm', '')
    full_region_name = f"{sido_nm} {sigungu_nm}" if (sido_nm and sigungu_nm) else default_prefix
    
    # Resolve administrative/legal dong mapping
    norm_dong = pure_dong.replace(" ", "")
    matched_group = None
    matched_key = None
    for k in DONG_GROUPS.keys():
        if norm_dong == k or norm_dong.replace("동", "") == k.replace("동", "") or normalize_h_dong_name(norm_dong) == normalize_h_dong_name(k):
            matched_group = DONG_GROUPS[k]
            matched_key = k
            break
            
    if matched_group:
        target_dongs = matched_group["dongs"]
        display_dong_name = matched_group["display"]
        target_admin_dong = matched_key if re.search(r'\d+동$', matched_key) else None
    else:
        if re.search(r'\d+동$', norm_dong) and bjdong_nm:
            clean_bjdong = re.sub(r'\d+동$', '동', bjdong_nm)
            target_dongs = [clean_bjdong]
            display_dong_name = f"{norm_dong} ({clean_bjdong})"
            target_admin_dong = norm_dong
        elif bjdong_nm:
            target_dongs = [bjdong_nm]
            display_dong_name = bjdong_nm
            target_admin_dong = None
        else:
            clean_bjdong = re.sub(r'\d+동$', '동', norm_dong)
            target_dongs = [clean_bjdong]
            display_dong_name = norm_dong
            target_admin_dong = None
            
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
            # [업데이트] 아파트 실거래가 수집은 생략 (개별 단지 조회 기능으로 이관)
                    
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
        save_admin_dong_cache()
            
    pass
                    
    report_lines = []
    
    def add_line(text=""):
        try:
            print(text)
        except Exception:
            try:
                print(text.encode('cp949', errors='replace').decode('cp949'))
            except Exception:
                pass
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
    

    def get_price_range(subset):
        prices = []
        for item in subset:
            val = str(item.get('dealAmount', '') or item.get('rowPrice', '') or item.get('deposit', '') or item.get('guaranteeAmt', '')).strip().replace(',', '')
            if val:
                try:
                    prices.append(float(val))
                except:
                    pass
        if not prices: return None
        min_p = min(prices)
        max_p = max(prices)
        if min_p == max_p: return local_format_price(min_p)
        return f"{local_format_price(min_p)} ~ {local_format_price(max_p)}"

    pass
    # Villa section
    for label, txs, prop_type in [("🏡 연립/다세대/빌라 (최근 6개월 기준)", filtered_villa_txs, '2')]:
        if not txs:
            add_line(f"\n[{label}] 실거래 데이터가 존재하지 않습니다.")
            continue
            
        add_line(f"\n[{label} 시장 동향 (방수 추정별 세분화)]")
        
        groups = {
            "원룸형 (전용 20㎡ 미만)": [],
            "투룸형 (전용 20~40㎡)": [],
            "쓰리룸 이상형 (전용 40㎡ 이상)": [],
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
                
        for grp_name in ["원룸형 (전용 20㎡ 미만)", "투룸형 (전용 20~40㎡)", "쓰리룸 이상형 (전용 40㎡ 이상)", "지하층 (반지하 전체)"]:
            g_txs = groups[grp_name]
            g_trades = [t for t in g_txs if t.get('_trade_type') == '매매']
            g_jeonses = [t for t in g_txs if t.get('_trade_type') == '전세']
            g_wolses = [t for t in g_txs if t.get('_trade_type') == '월세']
            
            g_trade_str = get_price_range(g_trades) or "-"
            g_jeonse_str = get_price_range(g_jeonses) or "-"
            g_overall_rate = calculate_market_conversion_rate(g_txs)
            
            g_rate_str = f"{g_overall_rate:.2f}%" if g_overall_rate else "-"
            
            add_line(f" • {grp_name}:")
            add_line(f"   - 거래 건수: 총 {len(g_txs)}건 (매매 {len(g_trades)} / 전세 {len(g_jeonses)} / 월세 {len(g_wolses)})")
            add_line(f"   - 매매가 (최저~최고): {g_trade_str} | 전세금 (최저~최고): {g_jeonse_str} | 전환율: {g_rate_str}")
            
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
        
    # 대지지분 평단가 5년 신축/구축 듀얼 분석 (모아타운/개발지 핵심 지표)
    land_stats = calculate_villa_land_bracket_stats(villa_txs)
    if land_stats and land_stats.get('brackets'):
        add_line("\n[🎯 개발지/모아타운 핵심 지표: 대지지분 구간별 평당가 분석 (최근 24개월 전수)]")
        add_line("  ※ 모아타운·재개발 투자 5년 보유 규정 및 노후도 기준 반영 (5년 이하 신축 vs 5년 초과 구축 비교)")
        add_line(f" {'구간':<15} | {'총건수':<6} | {'구축(>5년) 평당가':<14} | {'신축(≤5년) 평당가':<14} | {'신축 프리미엄':<10}")
        add_line(" " + "-" * 68)
        for b in land_stats['brackets']:
            tot_cnt = b['old_cnt'] + b['new_cnt']
            cnt_str = f"{tot_cnt}건"
            old_str = b['old_str'] if b['old_cnt'] > 0 else "-"
            new_str = b['new_str'] if b['new_cnt'] > 0 else "-"
            diff_str = b['gap_str'] if b['gap_str'] != "-" else "-"
            add_line(f"  {b['label']:<13} | {cnt_str:<6} | {old_str:<14} | {new_str:<14} | {diff_str:<10}")
        add_line(" " + "-" * 68)

    # CMA 추천 매물 (Best Value Pick) - 공인중개사법 준수 매물 실시간 점검 (방법 B)
    refresh_mode = check_and_refresh_serve_listings()
    cma_picks = []
    if refresh_mode != "skip":
        cma_picks = select_cma_recommended_listings(display_dong_name, filtered_villa_txs, max_picks=2)

    if cma_picks:
        add_line("\n[📌 CMA 시세 분석 기반 이달의 추천 매물 (Best Value Pick)]")
        add_line(" ※ 최근 6개월 국토교통부 실거래 데이터 대비 가격 경쟁력이 검증된 엄선 매물입니다.")
        for idx, p in enumerate(cma_picks, 1):
            short_addr = p['address'].replace("서울특별시 ", "").replace("서울시 ", "")
            flr_disp = p['floor_info'].split('/')[0].strip() if '/' in p['floor_info'] else p['floor_info']
            if not flr_disp: flr_disp = "지상층"
            add_line(f"\n • [추천 {idx}] [{p['trade_type']}] {p['prop_type']} ({short_addr}) - 전용 {p['excl_area']:.1f}㎡ / {flr_disp}")
            add_line(f"   - 금  액: {p['price_display']}")
            add_line(f"   - CMA 분석 근거: {p['cma_reason']}")
            feat_str = p['feature']
            if p.get('move_in'):
                feat_str += f" (입주: {p['move_in']})"
            add_line(f"   - 주요 특징: {feat_str}")
        add_line("\n" + "-" * 50)
        
    # Save Report files
    os.makedirs("reports", exist_ok=True)
    base_filename = f"reports/동향분석_{file_safe_dong}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    txt_filename = f"{base_filename}.txt"
    pdf_filename = f"{base_filename}.pdf"
    
    # Save TXT
    try:
        with open(txt_filename, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
        print(f"\n[저장 완료] 텍스트 보고서 저장 완료: {os.path.abspath(txt_filename)}")
    except Exception as e:
        print(f"\n [!] 텍스트 보고서 저장 실패: {e}")
        
    # Generate & Save PDF
    try:
        member_info = load_member_info()
        generate_market_report_pdf(pdf_filename, display_dong_name, villa_txs, member_info, region_prefix=full_region_name, cma_picks=cma_picks)
        print(f"[발행 완료] PDF 보고서 발행 완료 (중개사 서명 포함): {os.path.abspath(pdf_filename)}")
        if sys.platform == "win32" and os.path.exists(pdf_filename):
            try:
                os.startfile(os.path.abspath(pdf_filename))
            except Exception:
                pass
    except Exception as e:
        print(f" [!] PDF 보고서 생성 실패: {e}")
        
    input("\n메뉴로 돌아가려면 엔터를 누르세요...")

if __name__ == "__main__":
    run_market_analysis()
