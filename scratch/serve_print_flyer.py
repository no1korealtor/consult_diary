import os
import sys
import json
import re
import urllib.request
import urllib.parse
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Import utilities from other modules in the workspace
from get_building_info import get_building_data, get_expos_data
from trade_viewer import get_kakao_address_info, classify_property_type

def load_member_info():
    """Loads member information from member_info.json."""
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
            return profile
        except Exception as e:
            print(f"[오류] member_info.json 읽기 실패: {e}")
    return {}

def format_korean_price(trade_type, price_str):
    """Formats raw price string to Korean standard notation."""
    if not price_str:
        return ""
    
    def format_val(val):
        if val >= 10000:
            eok = val // 10000
            man = val % 10000
            if man > 0:
                return f"{eok}억 {man:,}만원"
            return f"{eok}억원"
        else:
            return f"{val:,}만원"

    if "/" in price_str:
        parts = price_str.split("/")
        dep = parts[0].strip().replace(",", "")
        rent = parts[1].strip().replace(",", "")
        try:
            dep_val = int(dep)
            rent_val = int(rent)
            return f"보증금 {format_val(dep_val)} / 월세 {format_val(rent_val)}"
        except:
            return f"보증금 {parts[0].strip()}만 / 월세 {parts[1].strip()}만"
    else:
        val_str = price_str.replace(",", "")
        try:
            val = int(val_str)
            return f"{trade_type} {format_val(val)}"
        except:
            return f"{trade_type} {price_str}"

def clean_area(area_info):
    """Extracts exclusive area in sqm from area_info string."""
    if not area_info:
        return ""
    if "/" in area_info:
        parts = area_info.split("/")
        excl = parts[1].replace("(㎡)", "").replace("㎡", "").strip()
        return excl
    else:
        excl = area_info.replace("(㎡)", "").replace("㎡", "").strip()
        return excl

def classify_listing(item):
    """Classifies listing into standard real estate newspaper categories."""
    prop_type = item.get("prop_type", "")
    trade_type = item.get("trade_type", "")
    address = item.get("address", "")
    feature = item.get("feature", "")
    area_info = item.get("area_info", "")
    
    # 1. Apartment
    if "아파트" in prop_type or "아파트" in address:
        if trade_type == "매매":
            return "아파트 (매매)"
        else:
            return "아파트 (전세/월세)"
            
    # 2. Commercial / Office / etc.
    if any(k in prop_type or k in feature or k in address for k in ["상가", "사무실", "점포", "상가점포", "토지", "공장"]):
        return "상가 / 사무실 / 기타"
        
    # 3. Room count classification for villas / houses
    rooms = 1
    excl_area = 0.0
    try:
        excl_str = clean_area(area_info)
        if excl_str:
            excl_area = float(excl_str)
    except:
        pass
        
    if any(k in feature for k in ["방3", "쓰리룸", "방 3"]):
        rooms = 3
    elif any(k in feature for k in ["방2", "투룸", "방 2"]):
        rooms = 2
    elif any(k in feature for k in ["원룸", "방1", "방 1", "분리형원룸"]):
        rooms = 1
    else:
        # Fallback based on area (sqm)
        if excl_area >= 50.0:
            rooms = 3
        elif excl_area >= 30.0:
            rooms = 2
        else:
            rooms = 1
            
    if rooms == 1 or "오피스텔" in prop_type:
        return "원룸 / 오피스텔"
    elif rooms == 2:
        return "빌라/주택 (방2개)"
    else:
        return "빌라/주택 (방3개 이상)"

def suggest_badge(item):
    """Automatically suggests a recommended badge based on property features and types."""
    feature = item.get("feature", "") or ""
    prop_type = item.get("prop_type", "") or ""
    address = item.get("address", "") or ""
    
    # 1. Bargain / price drop
    if any(k in feature for k in ["급매", "가격인하", "급전세", "가격절충", "급매물", "초급매"]):
        return "🔥 급매"
    
    # 2. Redevelopment / Moatown investment
    if any(k in feature or k in address for k in ["모아타운", "재개발", "조합", "재건축", "가로주택"]):
        return "🚧 재개발"
        
    # 3. Premium features
    if any(k in feature for k in ["특올수리", "올수리", "리모델링", "첫입주", "신축급", "풀옵션"]):
        return "💎 특급추천"
        
    # 4. CMA Recommended tag (approx 15% of listings randomly)
    import random
    if random.random() < 0.15:
        return "⭐ CMA 추천"
        
    return ""

def make_ad_text(item, office_phone):
    """Builds short, informative paragraph suitable for newspaper-style classified ads."""
    addr = item.get("address", "")
    addr_short = addr.replace("서울특별시", "").replace("마포구", "").strip()
    
    flr_info = item.get("floor_info", "")
    if "/" in flr_info:
        flr = flr_info.split("/")[0].strip()
    else:
        flr = flr_info
        
    area = item.get("area_info", "").replace("(㎡)", "㎡").replace("㎡", "").strip()
    if "/" in area:
        area = area.split("/")[1].strip() + "㎡"
    elif area:
        area = area + "㎡"
        
    trade_type = item.get("trade_type", "")
    price_str = item.get("price_str", "")
    price_formatted = format_korean_price(trade_type, price_str)
    
    feature = item.get("feature", "")
    move_in = item.get("move_in", "")
    
    desc = f"<b>[{addr_short}]</b> "
    details = []
    if flr:
        details.append(f"{flr}")
    if area:
        details.append(f"{area}")
    if price_formatted:
        details.append(f"<span style='color:#0284c7; font-weight:700;'>{price_formatted}</span>")
    
    desc += ", ".join(details)
    
    extra = []
    if move_in:
        extra.append(f"입주: {move_in}")
    if feature:
        extra.append(feature)
        
    if extra:
        desc += ". " + ", ".join(extra)
        
    return desc

def run_serve_print_flyer():
    print("==================================================")
    print(" 🖨️ 부동산써브 매물 광고 전단지(A4) 인쇄 도구 ")
    print("==================================================")
    
    import serve_auto_upload
    driver = None
    
    if serve_auto_upload._kept_alive_driver is not None:
        try:
            _ = serve_auto_upload._kept_alive_driver.current_url
            driver = serve_auto_upload._kept_alive_driver
            print(" -> 기존에 열린 부동산써브 크롬 브라우저를 재사용합니다.")
        except Exception:
            serve_auto_upload._kept_alive_driver = None

    if driver is None:
        options = Options()
        options.add_experimental_option("detach", True)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        driver = webdriver.Chrome(options=options)
        serve_auto_upload._kept_alive_driver = driver
        
    try:
        current_url = driver.current_url
        if "ma.serve.co.kr/good/articleRegistList" not in current_url:
            driver.get("https://ma.serve.co.kr/good/articleRegistList")
    except Exception:
        driver.get("https://ma.serve.co.kr/good/articleRegistList")
    
    print("\n[안내] 크롬 브라우저에서 부동산써브 로그인 후")
    print("       '통합매물관리' 목록 화면이 보이도록 준비해 주세요.")
    
    while True:
        print("\n" + "="*50)
        user_input = input(" 매물 목록 화면이 열렸으면 엔터(Enter)를 치세요 (종료: 'q'): ")
        
        if user_input.strip().lower() == 'q':
            break
            
        print("\n화면에서 등록된 매물을 스캔 중입니다...")
        
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
                
                naver_id = ""
                naver_match = re.search(r'\b(2\d{9})\b', text)
                if naver_match:
                    naver_id = naver_match.group(1)
                
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
            except Exception as e:
                pass
                
        if not listings:
            print("  ❌ 화면에서 파싱된 매물이 없습니다. 브라우저 목록 화면을 열어주세요.")
            continue
            
        print(f" -> 성공적으로 {len(listings)}개의 매물을 스캔하였습니다!")
        
        # Load broker profile
        broker_profile = load_member_info()
        office_phone = broker_profile.get("phone", "02-375-4489")
        
        # Construct listings data for JS
        js_listings = []
        for idx, item in enumerate(listings, 1):
            cat = classify_listing(item)
            desc = make_ad_text(item, office_phone)
            js_listings.append({
                "id": idx,
                "category": cat,
                "text": desc,
                "badge": suggest_badge(item),
                "enabled": True
            })
            
        # Write flyer.html
        generate_flyer_html(js_listings, broker_profile)
        
        # Open browser
        base_dir = os.path.dirname(os.path.abspath(__file__))
        flyer_path = os.path.join(base_dir, "..", "flyer.html")
        abs_flyer_path = os.path.abspath(flyer_path)
        
        webbrowser.open(f"file:///{abs_flyer_path}")
        print("\n" + "="*50)
        print(" 🎉 A4 벼룩시장식 대량 광고지 편집창이 브라우저에 열렸습니다!")
        print(f" 저장 위치: {abs_flyer_path}")
        print(" 브라우저의 왼쪽 편집창에서 매물 분류 수정, 내용 다듬기, 추가/삭제,")
        print(" 글씨 크기 및 줄 간격을 조절하여 A4 한 장에 맞추어 인쇄하실 수 있습니다.")
        print("="*50)
        input("\n돌아가시려면 엔터(Enter)를 누르세요...")

def generate_flyer_html(js_listings, broker):
    office_name = broker.get("office_name", "신대림공인중개사사무소")
    office_address = broker.get("office_address", "서울 마포구 성산동 137-21")
    
    # Extract phone numbers
    raw_phone = broker.get("phone", "010-9128-0586")
    if raw_phone == "01091280586":
        mobile_phone = "010-9128-0586"
    else:
        mobile_phone = raw_phone
        
    office_phone = "02-375-4489" # Default Shindaelim landline
    
    reg_number = broker.get("registration_number", "92380000-4131")
    rep_name = broker.get("name", "조항준")

    listings_json = json.dumps(js_listings, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>부동산 A4 매물 광고판 (벼룩시장형)</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        :root {{
            --font-size: 8.5px;
            --line-height: 1.35;
            --page-padding: 12mm;
            --column-count: 3;
        }}
        body {{
            font-family: 'Noto Sans KR', sans-serif;
            background-color: #f1f5f9;
            color: #1e293b;
            display: flex;
            min-height: 100vh;
        }}
        
        /* Sidebar layout for editing */
        .sidebar {{
            width: 460px;
            background-color: #0f172a;
            color: #f8fafc;
            padding: 20px;
            overflow-y: auto;
            height: 100vh;
            position: fixed;
            left: 0;
            top: 0;
            box-shadow: 4px 0 15px rgba(0,0,0,0.2);
            z-index: 100;
        }}
        .sidebar h2 {{
            font-size: 1.2rem;
            margin-bottom: 15px;
            color: #38bdf8;
            font-weight: 700;
            border-bottom: 1px solid #334155;
            padding-bottom: 10px;
        }}
        .form-group {{
            margin-bottom: 12px;
        }}
        .form-group label {{
            display: block;
            font-size: 0.75rem;
            font-weight: 500;
            margin-bottom: 4px;
            color: #94a3b8;
        }}
        .form-group input, .form-group textarea, .form-group select {{
            width: 100%;
            padding: 8px;
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 4px;
            color: #f8fafc;
            font-family: inherit;
            font-size: 0.85rem;
        }}
        .form-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}
        .slider-group {{
            background: #1e293b;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 15px;
        }}
        .slider-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        .slider-row:last-child {{
            margin-bottom: 0;
        }}
        .slider-row label {{
            font-size: 0.75rem;
            color: #94a3b8;
            width: 100px;
        }}
        .slider-row input[type="range"] {{
            flex: 1;
            margin: 0 10px;
        }}
        .slider-value {{
            font-size: 0.75rem;
            color: #38bdf8;
            width: 35px;
            text-align: right;
        }}
        
        .btn-action {{
            display: block;
            width: 100%;
            padding: 10px;
            background: linear-gradient(135deg, #0284c7, #0369a1);
            color: white;
            font-weight: 700;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            margin-top: 15px;
            text-align: center;
            transition: all 0.2s;
        }}
        .btn-action:hover {{
            background: linear-gradient(135deg, #0369a1, #075985);
        }}
        .btn-add-ad {{
            background: linear-gradient(135deg, #10b981, #059669);
            margin-bottom: 15px;
        }}
        .btn-add-ad:hover {{
            background: linear-gradient(135deg, #059669, #047857);
        }}
        
        /* Listings list in sidebar */
        .listing-card {{
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 10px;
            position: relative;
        }}
        .card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        .card-header label {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.8rem;
            font-weight: 600;
            color: #f8fafc;
            cursor: pointer;
        }}
        .card-controls {{
            display: flex;
            gap: 5px;
        }}
        .btn-icon {{
            background: none;
            border: none;
            color: #94a3b8;
            cursor: pointer;
            padding: 2px 4px;
            font-size: 0.8rem;
        }}
        .btn-icon:hover {{
            color: #f8fafc;
        }}
        .btn-delete:hover {{
            color: #ef4444;
        }}
        
        /* Main Preview Container */
        .preview-container {{
            margin-left: 460px;
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 40px;
            background-color: #e2e8f0;
            overflow-y: auto;
            height: 100vh;
        }}
        
        /* A4 Page Styling */
        .a4-page {{
            width: 210mm;
            min-height: 297mm;
            background-color: white;
            padding: var(--page-padding);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
        }}
        
        /* Header styling */
        .page-header {{
            border-bottom: 2px solid #0f172a;
            padding-bottom: 10px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header-left {{
            text-align: left;
        }}
        .page-title {{
            font-size: 22px;
            font-weight: 900;
            color: #0f172a;
            letter-spacing: 2px;
            margin-bottom: 4px;
            line-height: 1.2;
        }}
        .header-subtitle {{
            font-size: 9px;
            color: #64748b;
            font-weight: 500;
        }}
        .header-right-cta {{
            background: #ef4444;
            color: white;
            border-radius: 6px;
            padding: 8px 16px;
            text-align: center;
            min-width: 200px;
            box-shadow: 0 4px 10px rgba(239, 68, 68, 0.2);
            border: 1px solid #dc2626;
        }}
        .header-cta-label {{
            font-size: 8px;
            color: #fee500;
            font-weight: 800;
            letter-spacing: 0.5px;
            margin-bottom: 2px;
            text-transform: uppercase;
        }}
        .header-cta-phone {{
            font-size: 16px;
            font-weight: 900;
            color: white;
            letter-spacing: 0.5px;
            line-height: 1.1;
        }}
        .header-cta-mobile {{
            font-size: 10px;
            font-weight: 700;
            color: white;
            opacity: 0.95;
            margin-top: 1px;
        }}
        .broker-info-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 7.5px;
            color: #475569;
            background-color: #f8fafc;
            border: 1px solid #cbd5e1;
            padding: 5px 10px;
            border-radius: 4px;
            margin-bottom: 12px;
        }}
        .broker-info-bar span {{
            font-weight: 500;
        }}
        .broker-info-bar strong {{
            color: #0284c7;
        }}
        
        /* Multi-column layout */
        .columns-container {{
            flex: 1;
            column-count: var(--column-count);
            column-gap: 12px;
            column-rule: 1px dashed #cbd5e1;
        }}
        
        /* Category block */
        .category-block {{
            break-inside: avoid;
            margin-bottom: 10px;
        }}
        .category-heading {{
            background-color: #1e293b;
            color: white;
            padding: 3px 6px;
            font-size: calc(var(--font-size) + 1px);
            font-weight: 700;
            margin-bottom: 6px;
            border-radius: 2px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .category-heading .count {{
            font-size: 0.8em;
            opacity: 0.8;
        }}
        
        /* Individual Listing Ads */
        .ad-list {{
            list-style: none;
            padding-left: 2px;
        }}
        .ad-item {{
            font-size: var(--font-size);
            line-height: var(--line-height);
            color: #1e293b;
            margin-bottom: 6px;
            border-bottom: 1px dotted #e2e8f0;
            padding-bottom: 4px;
            word-break: break-all;
        }}
        .ad-item:last-child {{
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }}
        .ad-item.highlighted-ad {{
            background-color: #fef08a !important;
            border-left: 2.5px solid #eab308;
            padding-left: 4px;
            font-weight: 500;
            border-radius: 1px;
        }}
        .badge-tag {{
            font-size: calc(var(--font-size) - 1px);
            font-weight: 700;
            color: white;
            padding: 1px 3px;
            border-radius: 2px;
            margin-right: 3px;
            display: inline-block;
            vertical-align: middle;
            line-height: 1.1;
        }}
        .badge-tag.cma {{ background-color: #0284c7; }}
        .badge-tag.hot {{ background-color: #ef4444; }}
        .badge-tag.redev {{ background-color: #8b5cf6; }}
        .badge-tag.best {{ background-color: #10b981; }}
        .badge-tag.below {{ background-color: #f59e0b; }}
        
        /* Footer signature */
        .page-footer {{
            border-top: 2px solid #cbd5e1;
            padding-top: 8px;
            margin-top: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 7.5px;
            color: #64748b;
        }}
        .footer-stamp {{
            font-size: 8px;
            font-weight: bold;
            color: #0f172a;
            border: 1px solid #0f172a;
            padding: 2px 6px;
            border-radius: 2px;
        }}
        
        /* Premium CTA Banner */
        .cta-banner {{
            background: #f8fafc;
            border: 2px solid #0f172a;
            border-radius: 6px;
            padding: 8px 12px;
            margin-top: 10px;
            position: relative;
            text-align: center;
            break-inside: avoid;
        }}
        .cta-banner-badge {{
            position: absolute;
            top: -9px;
            left: 20px;
            background: #0f172a;
            color: #38bdf8;
            font-size: 8px;
            font-weight: 800;
            padding: 2px 8px;
            border-radius: 4px;
            letter-spacing: 0.5px;
        }}
        .cta-banner-text {{
            font-size: 9px;
            font-weight: 700;
            color: #334155;
            margin-bottom: 5px;
            line-height: 1.4;
        }}
        .cta-banner-phones {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            font-size: 14px;
            font-weight: 800;
            color: #0f172a;
        }}
        .cta-phone-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .cta-phone-label {{
            font-size: 8px;
            color: white;
            font-weight: 700;
            background: #ef4444;
            padding: 1px 4px;
            border-radius: 3px;
            line-height: 1.1;
        }}
        
        /* Accordion for categories in sidebar */
        .accordion-header {{
            background: #1e293b;
            color: #f8fafc;
            padding: 8px 12px;
            margin-bottom: 5px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            font-size: 0.8rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .accordion-content {{
            display: none;
            padding-left: 5px;
            margin-bottom: 10px;
        }}
        .accordion-content.active {{
            display: block;
        }}
        
        /* Print Styles */
        @media print {{
            body {{
                background-color: white;
            }}
            .sidebar {{
                display: none;
            }}
            .preview-container {{
                margin-left: 0;
                padding: 0;
                background-color: white;
                height: auto;
                overflow: visible;
            }}
            .a4-page {{
                box-shadow: none;
                margin: 0;
                width: 210mm;
                height: auto;
                min-height: 297mm;
            }}
        }}
    </style>
</head>
<body>

    <!-- Sidebar Editor Panel -->
    <div class="sidebar">
        <h2>📰 벼룩시장식 매물 광고지 편집</h2>
        
        <div class="form-group">
            <label for="input_global_title">광고지 타이틀</label>
            <input type="text" id="input_global_title" value="오늘의 추천 매물 정보" oninput="updateGlobalTitle(this.value)">
        </div>
        
        <div class="form-row">
            <div class="form-group">
                <label for="input_office_name">중개업소 상호</label>
                <input type="text" id="input_office_name" value="{office_name}" oninput="updateBrokerInfo()">
            </div>
            <div class="form-group">
                <label for="input_rep_name">대표자명</label>
                <input type="text" id="input_rep_name" value="{rep_name}" oninput="updateBrokerInfo()">
            </div>
        </div>
        
        <div class="form-row">
            <div class="form-group">
                <label for="input_office_phone">대표 연락처 (유선)</label>
                <input type="text" id="input_office_phone" value="{office_phone}" oninput="updateBrokerInfo()">
            </div>
            <div class="form-group">
                <label for="input_mobile_phone">휴대폰 연락처 (무선)</label>
                <input type="text" id="input_mobile_phone" value="{mobile_phone}" oninput="updateBrokerInfo()">
            </div>
        </div>
        
        <div class="form-row">
            <div class="form-group" style="grid-column: span 2;">
                <label for="input_reg_number">중개 등록번호</label>
                <input type="text" id="input_reg_number" value="{reg_number}" oninput="updateBrokerInfo()">
            </div>
        </div>
        
        <div class="form-group">
            <label for="input_office_address">사무소 소재지</label>
            <input type="text" id="input_office_address" value="{office_address}" oninput="updateBrokerInfo()">
        </div>

        <div class="form-group">
            <label for="input_cta_text">하단 홍보 문구 (Call-To-Action)</label>
            <textarea id="input_cta_text" rows="2" oninput="updateCtaText(this.value)">💡 찾으시는 조건(위치, 금액, 입주 시기 등)을 문자나 전화로 말씀해 주시면, 최적의 매물을 매칭해 드립니다!</textarea>
        </div>
        
        <!-- Print Layout Sliders -->
        <div class="slider-group">
            <div class="slider-row">
                <label>글자 크기 (Font)</label>
                <input type="range" id="slider_font" min="7" max="14" step="0.5" value="8.5" oninput="adjustStyle('font-size', this.value + 'px', 'val_font')">
                <span class="slider-value" id="val_font">8.5px</span>
            </div>
            <div class="slider-row">
                <label>줄 간격 (Line)</label>
                <input type="range" id="slider_line" min="1.1" max="1.8" step="0.05" value="1.35" oninput="adjustStyle('line-height', this.value, 'val_line')">
                <span class="slider-value" id="val_line">1.35</span>
            </div>
            <div class="slider-row">
                <label>열 개수 (Columns)</label>
                <select id="select_cols" onchange="adjustStyle('column-count', this.value, null)" style="width:70px; padding:3px; font-size:11px;">
                    <option value="2">2열</option>
                    <option value="3" selected>3열</option>
                    <option value="4">4열</option>
                </select>
            </div>
            <div class="slider-row">
                <label>용지 여백 (Margin)</label>
                <input type="range" id="slider_margin" min="5" max="25" step="1" value="12" oninput="adjustStyle('page-padding', this.value + 'mm', 'val_margin')">
                <span class="slider-value" id="val_margin">12mm</span>
            </div>
        </div>
        
        <button class="btn-action btn-add-ad" onclick="addNewListing()">➕ 새 매물 광고 추가하기</button>
        
        <!-- Accordion grouped Listings -->
        <div id="listings_accordion_container"></div>
        
        <button class="btn-action" onclick="window.print()" style="margin-top:20px; font-size:1.1rem; padding:12px;">🖨️ 광고지 인쇄하기</button>
    </div>

    <!-- Main Live Preview Container -->
    <div class="preview-container">
        <div class="a4-page" id="a4_page_el">
            
            <!-- Page Header -->
            <div class="page-header">
                <div class="header-left">
                    <h1 class="page-title" id="preview_global_title">오늘의 추천 매물 정보</h1>
                    <div class="header-subtitle">실시간 업데이트 매물 • 신뢰받는 맞춤 중개 서비스</div>
                </div>
                <div class="header-right-cta">
                    <div class="header-cta-label">📞 매물 상담 및 문의</div>
                    <div class="header-cta-phone" id="preview_broker_phone_header">{office_phone}</div>
                    <div class="header-cta-mobile" id="preview_broker_mobile_header">H.P: {mobile_phone}</div>
                </div>
            </div>
            
            <div class="broker-info-bar">
                <div>상호: <span id="preview_broker_name">{office_name}</span></div>
                <div>등록번호: <span id="preview_broker_reg">{reg_number}</span></div>
                <div>대표: <span id="preview_broker_rep">{rep_name}</span></div>
                <div>연락처: <strong id="preview_broker_phone">{office_phone}</strong></div>
                <div>일자: <span id="preview_date"></span></div>
            </div>
            
            <!-- Columns Listing Container -->
            <div class="columns-container" id="preview_columns_container">
                <!-- Grouped categories will be dynamically rendered here -->
            </div>
            
            <!-- Premium CTA Banner -->
            <div class="cta-banner">
                <div class="cta-banner-badge">상담 안내</div>
                <div class="cta-banner-text" id="preview_cta_text">💡 찾으시는 조건(위치, 금액, 입주 시기 등)을 문자나 전화로 말씀해 주시면, 최적의 매물을 매칭해 드립니다!</div>
                <div class="cta-banner-phones">
                    <div class="cta-phone-item">
                        <span class="cta-phone-label">유선전화</span>
                        <span id="preview_broker_phone_cta">{office_phone}</span>
                    </div>
                    <div class="cta-phone-item">
                        <span class="cta-phone-label">휴대폰</span>
                        <span id="preview_broker_mobile_cta">{mobile_phone}</span>
                    </div>
                </div>
            </div>
            
            <!-- Page Footer -->
            <div class="page-footer">
                <span id="preview_broker_address">사무소 주소: {office_address}</span>
                <span class="footer-stamp" id="preview_broker_stamp">{office_name}</span>
            </div>
            
        </div>
    </div>

    <script>
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        document.getElementById('preview_date').innerText = year + '년 ' + month + '월 ' + day + '일';
        
        let listings = {listings_json};
        
        const categories = [
            "아파트 (매매)",
            "아파트 (전세/월세)",
            "빌라/주택 (방3개 이상)",
            "빌라/주택 (방2개)",
            "원룸 / 오피스텔",
            "상가 / 사무실 / 기타"
        ];
        
        let accordionStates = {{}};
        categories.forEach(cat => {{
            accordionStates[cat] = true;
        }});
        
        function render() {{
            renderSidebar();
            renderPreview();
        }}
        
        function renderSidebar() {{
            const container = document.getElementById('listings_accordion_container');
            container.innerHTML = '';
            
            categories.forEach(cat => {{
                const catListings = listings.filter(item => item.category === cat);
                
                const accHeader = document.createElement('div');
                accHeader.className = 'accordion-header';
                accHeader.innerHTML = '<span>' + cat + ' (' + catListings.length + ')</span> <span>' + (accordionStates[cat] ? '▼' : '▶') + '</span>';
                accHeader.onclick = () => {{
                    accordionStates[cat] = !accordionStates[cat];
                    render();
                }};
                container.appendChild(accHeader);
                
                const accContent = document.createElement('div');
                accContent.className = 'accordion-content' + (accordionStates[cat] ? ' active' : '');
                
                catListings.forEach((item, idx) => {{
                    const card = document.createElement('div');
                    card.className = 'listing-card';
                    if (!item.enabled) card.style.opacity = '0.5';
                    
                    let optionsHtml = '';
                    categories.forEach(c => {{
                        const selectedAttr = (c === item.category) ? 'selected' : '';
                        optionsHtml += '<option value="' + c + '" ' + selectedAttr + '>' + c + '</option>';
                    }});
                    
                    card.innerHTML = 
                        '<div class="card-header">' +
                        '    <label>' +
                        '        <input type="checkbox" ' + (item.enabled ? 'checked' : '') + ' onchange="toggleListing(' + item.id + ')">' +
                        '        #' + item.id + ' 매물 활성화' +
                        '    </label>' +
                        '    <div class="card-controls">' +
                        '        <button class="btn-icon" onclick="moveListing(' + item.id + ', -1)">▲</button>' +
                        '        <button class="btn-icon" onclick="moveListing(' + item.id + ', 1)">▼</button>' +
                        '        <button class="btn-icon btn-delete" onclick="deleteListing(' + item.id + ')">🗑</button>' +
                        '    </div>' +
                        '</div>' +
                        '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px;">' +
                        '    <div class="form-group" style="margin-bottom:0;">' +
                        '        <label>분류</label>' +
                        '        <select onchange="updateListingCategory(' + item.id + ', this.value)" style="background:#1e293b; color:white; border:1px solid #334155; padding:4px; font-size:11px; width:100%;">' +
                                     optionsHtml +
                        '        </select>' +
                        '    </div>' +
                        '    <div class="form-group" style="margin-bottom:0;">' +
                        '        <label>추천 마킹</label>' +
                        '        <select onchange="updateListingBadge(' + item.id + ', this.value)" style="background:#1e293b; color:white; border:1px solid #334155; padding:4px; font-size:11px; width:100%;">' +
                        '            <option value="" ' + (!item.badge ? 'selected' : '') + '>(없음)</option>' +
                        '            <option value="⭐ CMA 추천" ' + (item.badge === "⭐ CMA 추천" ? 'selected' : '') + '>⭐ CMA 추천</option>' +
                        '            <option value="🔥 급매" ' + (item.badge === "🔥 급매" ? 'selected' : '') + '>🔥 급매</option>' +
                        '            <option value="💎 특급추천" ' + (item.badge === "💎 특급추천" ? 'selected' : '') + '>💎 특급</option>' +
                        '            <option value="⚡ 실거래가이하" ' + (item.badge === "⚡ 실거래가이하" ? 'selected' : '') + '>⚡ 실거래가 이하</option>' +
                        '            <option value="🚧 재개발" ' + (item.badge === "🚧 재개발" ? 'selected' : '') + '>🚧 투자 추천</option>' +
                        '        </select>' +
                        '    </div>' +
                        '</div>' +
                        '<div class="form-group" style="margin-bottom:0;">' +
                        '    <label>광고 문구 (HTML 사용 가능)</label>' +
                        '    <textarea rows="3" oninput="updateListingText(' + item.id + ', this.value)" style="font-size:11px;">' + item.text + '</textarea>' +
                        '</div>';
                    accContent.appendChild(card);
                }});
                container.appendChild(accContent);
            }});
        }}
        
        function renderPreview() {{
            const container = document.getElementById('preview_columns_container');
            container.innerHTML = '';
            
            categories.forEach(cat => {{
                const catListings = listings.filter(item => item.category === cat && item.enabled);
                if (catListings.length === 0) return;
                
                const block = document.createElement('div');
                block.className = 'category-block';
                
                const heading = document.createElement('div');
                heading.className = 'category-heading';
                heading.innerHTML = '<span>■ ' + cat + '</span> <span class="count">' + catListings.length + '건</span>';
                block.appendChild(heading);
                
                const list = document.createElement('ul');
                list.className = 'ad-list';
                
                catListings.forEach((item, idx) => {{
                    const li = document.createElement('li');
                    li.className = 'ad-item';
                    
                    let badgeHtml = '';
                    if (item.badge) {{
                        let badgeClass = 'hot';
                        if (item.badge.includes('CMA')) badgeClass = 'cma';
                        else if (item.badge.includes('급매')) badgeClass = 'hot';
                        else if (item.badge.includes('특급')) badgeClass = 'best';
                        else if (item.badge.includes('실거래')) badgeClass = 'below';
                        else if (item.badge.includes('재개발')) badgeClass = 'redev';
                        
                        badgeHtml = '<span class="badge-tag ' + badgeClass + '">' + item.badge + '</span>';
                        li.className += ' highlighted-ad';
                    }}
                    
                    li.innerHTML = (idx + 1) + '. ' + badgeHtml + item.text;
                    list.appendChild(li);
                }});
                block.appendChild(list);
                container.appendChild(block);
            }});
        }}
        
        function toggleListing(id) {{
            const item = listings.find(i => i.id === id);
            if (item) {{
                item.enabled = !item.enabled;
                renderPreview();
                renderSidebar();
            }}
        }}
        
        function updateListingText(id, value) {{
            const item = listings.find(i => i.id === id);
            if (item) {{
                item.text = value;
                renderPreview();
            }}
        }}
        
        function updateListingCategory(id, value) {{
            const item = listings.find(i => i.id === id);
            if (item) {{
                item.category = value;
                render();
            }}
        }}
        
        function updateListingBadge(id, value) {{
            const item = listings.find(i => i.id === id);
            if (item) {{
                item.badge = value;
                render();
            }}
        }}
        
        function deleteListing(id) {{
            if (confirm('이 매물을 삭제하시겠습니까?')) {{
                listings = listings.filter(i => i.id !== id);
                render();
            }}
        }}
        
        function moveListing(id, direction) {{
            const idx = listings.findIndex(i => i.id === id);
            if (idx === -1) return;
            const targetIdx = idx + direction;
            if (targetIdx < 0 || targetIdx >= listings.length) return;
            
            const temp = listings[idx];
            listings[idx] = listings[targetIdx];
            listings[targetIdx] = temp;
            render();
        }}
        
        function addNewListing() {{
            const maxId = listings.reduce((max, item) => item.id > max ? item.id : max, 0);
            listings.unshift({{
                id: maxId + 1,
                category: "원룸 / 오피스텔",
                text: "<b>[성산동 신축]</b> 1.5층 전용22㎡. <b>월세 1000/60</b>. 풀옵션, 조용한 주택가.",
                badge: "",
                enabled: true
            }});
            render();
        }}
        
        function updateGlobalTitle(val) {{
            document.getElementById('preview_global_title').innerText = val;
        }}
        
        function updateBrokerInfo() {{
            const officeName = document.getElementById('input_office_name').value;
            const repName = document.getElementById('input_rep_name').value;
            const officePhone = document.getElementById('input_office_phone').value;
            const mobilePhone = document.getElementById('input_mobile_phone').value;
            const regNumber = document.getElementById('input_reg_number').value;
            const officeAddress = document.getElementById('input_office_address').value;
            
            document.getElementById('preview_broker_name').innerText = officeName;
            document.getElementById('preview_broker_rep').innerText = repName;
            document.getElementById('preview_broker_phone').innerText = officePhone;
            document.getElementById('preview_broker_reg').innerText = regNumber;
            document.getElementById('preview_broker_address').innerText = '사무소 주소: ' + officeAddress;
            document.getElementById('preview_broker_stamp').innerText = officeName;

            const elHeaderPhone = document.getElementById('preview_broker_phone_header');
            if (elHeaderPhone) elHeaderPhone.innerText = officePhone;
            
            const elHeaderMobile = document.getElementById('preview_broker_mobile_header');
            if (elHeaderMobile) elHeaderMobile.innerText = 'H.P: ' + mobilePhone;
            
            const elCtaPhone = document.getElementById('preview_broker_phone_cta');
            if (elCtaPhone) elCtaPhone.innerText = officePhone;
            
            const elCtaMobile = document.getElementById('preview_broker_mobile_cta');
            if (elCtaMobile) elCtaMobile.innerText = mobilePhone;
        }}

        function updateCtaText(val) {{
            document.getElementById('preview_cta_text').innerText = val;
        }}
        
        function adjustStyle(property, value, displayId) {{
            document.documentElement.style.setProperty('--' + property, value);
            if (displayId) {{
                document.getElementById(displayId).innerText = value;
            }}
        }}
        
        render();
    </script>
</body>
</html>
"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    flyer_path = os.path.join(base_dir, "..", "flyer.html")
    with open(flyer_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
