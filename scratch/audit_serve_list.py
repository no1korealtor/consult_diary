import time
import urllib.request
import urllib.parse
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By

from get_building_info import get_building_data, get_expos_data
from trade_viewer import (
    get_kakao_address_info,
    get_recent_transactions,
    classify_property_type,
    get_cma_ref_price
)

def get_floor_category(floor_str):
    if not floor_str:
        return 'upper'
    try:
        f = int(floor_str)
        if f < 0:
            return 'base'
        elif f == 1:
            return 'first'
        else:
            return 'upper'
    except:
        return 'upper'

def local_format_price(val):
    if val >= 10000:
        eok = int(val // 10000)
        man = int(val % 10000)
        return f"{eok}억 {man:,}만" if man > 0 else f"{eok}억"
    else:
        return f"{int(val):,}만"

def calculate_market_conversion_rate(transactions):
    """
    transactions 목록에서 전세 거래와 월세 거래의 평균값을 기반으로
    시장 실제 전월세 전환율(%)을 산출합니다.
    """
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



def run_audit_serve_list():
    print("==================================================")
    print(" ️‍♂️ 부동산써브 [목록 스캔형] 자동 검증 봇 실행 ")
    print("==================================================")
    
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    
    driver.get("https://ma.serve.co.kr/good/articleRegistList")
    
    print("\n[1] 크롬 창이 열렸습니다. 로그인을 진행해 주세요.")
    print("[2] '통합매물관리' 목록 창을 열어 매물들이 화면에 보이게 해주세요.")
    
    do_cma = input("\n[선택] 매물 검증 시 CMA 시세 분석 및 가격 의견 조회를 함께 진행하시겠습니까? (y/n) [기본값: n]: ").strip().lower()
    enable_cma = (do_cma == 'y')
    
    while True:
        print("\n" + "="*50)
        user_input = input(" 목록 화면이 준비되었으면 엔터(Enter)를 치세요 (종료: 'q'): ")
        
        if user_input.strip().lower() == 'q':
            break
            
        print("\n화면에 보이는 모든 매물을 스캔합니다! 삐리릭- ")
        
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
        except:
            print("화면 텍스트를 읽어오지 못했습니다.")
            continue
            
        # 1. 주소 및 호수 파싱
        # 예: "주택 서울특별시 마포구 성산동 135-28" 또는 "제3층 제304호 3층 / 3층"
        
        lines = body_text.split('\n')
        
        listings = []
        current_listing = {}
        
        for line in lines:
            # 주소 감지 (주택, 아파트 등의 단어가 분리되어 있을 수 있으므로 주소 자체만 매칭)
            addr_match = re.search(r'(서울특별시\s+[가-힣]+구\s+[가-힣]+동\s*[0-9]+(?:-[0-9]+)?)', line)
            if addr_match:
                if current_listing.get('address'):
                    listings.append(current_listing)
                    current_listing = {}
                current_listing['address'] = addr_match.group(1).strip()
                
            if 'address' in current_listing:
                # 호수 감지 (제3층 제304호)
                ho_match = re.search(r'(?:제)?([0-9]+)호', line)
                if ho_match and 'ho' not in current_listing:
                    current_listing['ho'] = ho_match.group(1)
                    
                # 층 및 면적 감지 (-1층 / 3층 25.00 / 25.00(㎡))
                # 64.20 / 48.15(㎡)
                area_match = re.search(r'([0-9.]+)\s*/\s*([0-9.]+)\s*\(㎡\)', line)
                if area_match:
                    current_listing['supply_area'] = area_match.group(1)
                    current_listing['excl_area'] = area_match.group(2)
                    
                floor_match = re.search(r'(-?[0-9]+)층\s*/\s*([0-9]+)층', line)
                if floor_match:
                    current_listing['floor'] = floor_match.group(1)
                    current_listing['total_floor'] = floor_match.group(2)
                    
                # 가격 정보 감지 (매매, 전세, 월세)
                price_trade_match = re.search(r'매매\s*([0-9,]+)', line)
                if price_trade_match:
                    current_listing['trade_type'] = '매매'
                    current_listing['price'] = price_trade_match.group(1).replace(',', '')
                
                price_jeonse_match = re.search(r'전세\s*([0-9,]+)', line)
                if price_jeonse_match:
                    current_listing['trade_type'] = '전세'
                    current_listing['price'] = price_jeonse_match.group(1).replace(',', '')
                
                price_wolse_match = re.search(r'월세\s*([0-9,]+)\s*/\s*([0-9,]+)', line)
                if price_wolse_match:
                    current_listing['trade_type'] = '월세'
                    current_listing['deposit'] = price_wolse_match.group(1).replace(',', '')
                    current_listing['monthly_rent'] = price_wolse_match.group(2).replace(',', '')
                    
        if current_listing.get('address'):
            listings.append(current_listing)
            
        print(f" 총 {len(listings)}개의 매물을 발견했습니다. 검증을 시작합니다...\n")
        
        for idx, item in enumerate(listings, 1):
            addr = item.get('address', '')
            ho = item.get('ho', '')
            reg_excl_area = item.get('excl_area', '')
            
            print(f"[{idx}] {addr} {ho+'호' if ho else ''}")
            
            # VWorld 조회
            query = urllib.parse.quote(addr)
            vworld_url = f"http://api.vworld.kr/req/search?service=search&request=search&version=2.0&crs=EPSG:900913&size=1&page=1&query={query}&type=address&category=parcel&format=json&errorformat=json&key=80194C85-0EE3-3220-A3C1-3268AD8756B9"
            
            try:
                req = urllib.request.Request(vworld_url)
                req.add_header('Referer', 'http://localhost')
                res = urllib.request.urlopen(req)
                vworld_data = json.loads(res.read().decode('utf-8'))
                
                items = vworld_data.get('response', {}).get('result', {}).get('items', [])
                if not items:
                    print("  ❌ VWorld 주소 검색 실패")
                    print("-" * 40)
                    continue
                    
                pnu = items[0].get('id', '')
                sigunguCd, bjdongCd, bun, ji = pnu[0:5], pnu[5:10], pnu[11:15], pnu[15:19]
                
                bldg_data = get_building_data(sigunguCd, bjdongCd, bun, ji)
                expos_data = get_expos_data(sigunguCd, bjdongCd, bun, ji, "", ho) if ho else None
                
                if not bldg_data:
                    print("  ❌ 건축물대장 데이터 없음")
                    print("-" * 40)
                    continue
                    
                off_area = expos_data.get('area', '') if expos_data else bldg_data.get('totArea', '')
                
                # 비교 로직
                try:
                    reg_f = float(reg_excl_area)
                    off_f = float(off_area)
                    match = (reg_f == off_f)
                except:
                    match = str(reg_excl_area) == str(off_area)
                    
                if match:
                    print(f"  ✅ [전용면적 일치] 등록값: {reg_excl_area}㎡ == 공식값: {off_area}㎡")
                else:
                    print(f"   [전용면적 불일치] 등록값: {reg_excl_area}㎡ != 공식값: {off_area}㎡ (다가구인 경우 정상일 수 있음)")
                    
                # CMA 시세 분석 및 가격 의견
                if enable_cma and 'trade_type' in item:
                    ttype = item['trade_type']
                    
                    # 1. Kakao address info 조회
                    addr_info = get_kakao_address_info(addr)
                    if not addr_info:
                        bjdong_nm = ""
                        dong_match = re.search(r'([가-힣]+동)', addr)
                        if dong_match:
                            bjdong_nm = dong_match.group(1)
                        addr_info = {
                            'sigunguCd': sigunguCd,
                            'bjdongCd': bjdongCd,
                            'bun': bun,
                            'ji': ji,
                            'bjdongNm': bjdong_nm
                        }
                    
                    # 2. 준공년도 추출
                    target_build_year = None
                    apr_year = bldg_data.get('aprYear', '')
                    if apr_year:
                        try:
                            target_build_year = int(apr_year)
                        except:
                            pass
                            
                    # 3. 부동산 유형 분류
                    prop_type = classify_property_type(
                        bldg_data.get('purpose', ''),
                        bldg_data.get('bldNm', ''),
                        bldg_data.get('etcPurps', '')
                    )
                    
                    # 4. 주거 유형 추출 (다가구 vs 단독)
                    target_house_type = None
                    if prop_type == '4':
                        combined = (bldg_data.get('purpose', '') + " " + bldg_data.get('bldNm', '') + " " + bldg_data.get('etcPurps', '')).lower()
                        if '다가구' in combined:
                            target_house_type = '다가구'
                        elif '단독' in combined:
                            target_house_type = '단독'
                            
                    # 5. 전용면적 파싱
                    try:
                        target_area = float(reg_excl_area)
                    except:
                        target_area = None
                        
                    # 6. 실거래 내역 조회
                    print(f"   🔍 [{ttype} 시세 분석] 실거래 데이터 조회 중...")
                    transactions = get_recent_transactions(
                        addr_info['sigunguCd'],
                        addr_info['bun'],
                        addr_info['ji'],
                        prop_type,
                        addr_info.get('bjdongNm'),
                        target_build_year,
                        target_house_type
                    )
                    if transactions is None:
                        transactions = []
                        
                    # 거래 내역이 부족할 시 자동으로 인근 유사 조건으로 확장
                    if len(transactions) < 3:
                        expanded_txs = get_recent_transactions(
                            addr_info['sigunguCd'],
                            addr_info['bun'],
                            addr_info['ji'],
                            prop_type,
                            addr_info.get('bjdongNm'),
                            target_build_year=target_build_year,
                            target_house_type=target_house_type,
                            expand_similar=True,
                            target_area=target_area,
                            build_year_margin=3,
                            area_margin=0.15
                        )
                        if expanded_txs:
                            transactions = expanded_txs
                            
                    # 7. CMA 기준가 계산
                    floor_cat = get_floor_category(item.get('floor', ''))
                    
                    reg_price = None
                    ref_price = None
                    ref_desc = None
                    
                    if ttype == '매매':
                        try:
                            reg_price = float(item['price'])
                            ref_price, ref_desc = get_cma_ref_price(transactions, floor_cat, is_rent=False, is_wolse=False)
                        except:
                            pass
                    elif ttype == '전세':
                        try:
                            reg_price = float(item['price'])
                            ref_price, ref_desc = get_cma_ref_price(transactions, floor_cat, is_rent=True, is_wolse=False)
                        except:
                            pass
                    elif ttype == '월세':
                        try:
                            dep_val = float(item.get('deposit', 0))
                            rent_val = float(item.get('monthly_rent', 0))
                            
                            # 시장 실제 전환율 계산 시도
                            market_rate = calculate_market_conversion_rate(transactions)
                            if market_rate:
                                # 1단계: 시장 실제 전환율 적용하여 환산가 계산
                                reg_price = dep_val + (rent_val * 12) / (market_rate / 100)
                                ref_price, ref_desc = get_cma_ref_price(transactions, floor_cat, is_rent=True, is_wolse=False)
                                if ref_price:
                                    ref_desc = f"{ref_desc} (시장 전환율 {market_rate:.2f}% 적용 환산)"
                                else:
                                    # 전세 실거래가가 없으면 2단계 fallback (100배수)
                                    reg_price = dep_val + rent_val * 100
                                    ref_price, ref_desc = get_cma_ref_price(transactions, floor_cat, is_rent=True, is_wolse=True)
                            else:
                                # 2단계 fallback (기본 100배수)
                                reg_price = dep_val + rent_val * 100
                                ref_price, ref_desc = get_cma_ref_price(transactions, floor_cat, is_rent=True, is_wolse=True)
                        except:
                            pass
                            
                    # 8. 비교 및 의견 출력
                    if reg_price is not None and ref_price is not None:
                        diff = reg_price - ref_price
                        ratio = (reg_price / ref_price - 1.0) * 100
                        
                        if ttype == '월세':
                            market_rate = calculate_market_conversion_rate(transactions)
                            if market_rate:
                                reg_price_str = f"보증금 {local_format_price(float(item['deposit']))}/월세 {item['monthly_rent']}만 (시장전환율 {market_rate:.2f}% 적용 환산 {local_format_price(reg_price)})"
                            else:
                                reg_price_str = f"보증금 {local_format_price(float(item['deposit']))}/월세 {item['monthly_rent']}만 (100배수 환산 {local_format_price(reg_price)})"
                            ref_price_str = f"환산 {local_format_price(ref_price)}"
                        else:
                            reg_price_str = local_format_price(reg_price)
                            ref_price_str = local_format_price(ref_price)
                            
                        print(f"   📊 [CMA 가격 비교]")
                        print(f"     - 등록가: {reg_price_str}")
                        print(f"     - 시세가: {ref_price_str} ({ref_desc})")
                        
                        if ratio > 10.0:
                            print(f"     - 의견: 📈 등록가가 시세 대비 약 {ratio:.1f}% 다소 높게 책정되었습니다.")
                        elif ratio < -10.0:
                            print(f"     - 의견: 📉 등록가가 시세 대비 약 {-ratio:.1f}% 다소 낮게 책정되었습니다.")
                        else:
                            print(f"     - 의견: ⚖️ 등록가가 시세 수준으로 적정하게 책정되었습니다.")
                    else:
                        print("   📊 [CMA 가격 비교] 실거래 또는 유사 거래 사례가 부족하여 시세 가격 분석 및 의견 작성이 불가합니다.")
                    
            except Exception as e:
                print(f"  ⚠️ 조회 중 에러 발생: {e}")
            print("-" * 40)
            
        print(" 현재 페이지 스캔 및 검증이 완료되었습니다. 다음 페이지로 넘어가신 후 다시 엔터를 치시면 계속 진행합니다!")

if __name__ == "__main__":
    run_audit_serve_list()
