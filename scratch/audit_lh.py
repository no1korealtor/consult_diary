import time
import urllib.request
import urllib.parse
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By

from get_building_info import get_building_data, get_expos_data

def run_audit_lh():
    print("==================================================")
    print(" 🕵️‍♂️ LH 매물 자동 검증 봇 (Audit Bot) 실행 ")
    print("==================================================")
    
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    
    driver.get("https://jeonse.lh.or.kr")
    
    print("\n[1] 크롬 창이 열렸습니다. 로그인을 진행해 주세요.")
    print("[2] 방금 등록하신 매물의 '수정(또는 상세조회)' 화면으로 이동해 주세요.")
    print("    (주소, 면적, 층수 등이 입력칸에 보이는 화면)")
    print("[3] 화면이 준비되면 이 까만 창에서 엔터를 쳐주세요!")
    
    input("\n화면 이동이 끝났으면 엔터(Enter)를 치세요...")
    
    print("\n화면에서 매물 정보를 훔쳐(?)오는 중입니다...")
    
    # iframe 전부 뒤지기
    addr_val = ""
    detail_val = ""
    registered_area = ""
    registered_floor = ""
    registered_year = ""
    
    found = False
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        
        def extract_data():
            try:
                return {
                    'addr': driver.find_element(By.ID, "rthousAddr").get_attribute("value"),
                    'detail': driver.find_element(By.ID, "detailAddr").get_attribute("value"),
                    'area': driver.find_element(By.ID, "rthousExclAr").get_attribute("value"),
                    'floor': driver.find_element(By.ID, "floor").get_attribute("value"),
                    'year': driver.find_element(By.ID, "rthousCompetDe").get_attribute("value")
                }
            except:
                return None
                
        # 1. 기본 화면 시도
        data = extract_data()
        if data and data['addr']:
            addr_val, detail_val = data['addr'], data['detail']
            registered_area, registered_floor, registered_year = data['area'], data['floor'], data['year']
            found = True
            break
            
        # 2. iframe 시도
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        for frame in frames:
            try:
                driver.switch_to.frame(frame)
                data = extract_data()
                if data and data['addr']:
                    addr_val, detail_val = data['addr'], data['detail']
                    registered_area, registered_floor, registered_year = data['area'], data['floor'], data['year']
                    found = True
                    break
            except:
                pass
            finally:
                driver.switch_to.default_content()
                
        if found: break
        
    if not found:
        print("❌ 주소 정보를 찾을 수 없습니다. 수정/상세 화면이 맞는지 확인해주세요!")
        return
        
    address_query = f"{addr_val} {detail_val}".strip()
    
    dong_name = ""
    ho_name = ""
    dong_match = re.search(r'([0-9가-힣]+)동', detail_val)
    ho_match = re.search(r'([0-9]+)호', detail_val)
    if not ho_match:
        nums = re.findall(r'([0-9]+)', detail_val)
        if nums: ho_name = nums[-1]
    else:
        ho_name = ho_match.group(1)
    if dong_match: dong_name = dong_match.group(1)

    print(f"\n✅ 화면 정보 파싱 완료!")
    print(f" -> 주소: {address_query}")
    print(f" -> 등록된 전용면적: {registered_area}㎡, 층수: {registered_floor}층, 준공일: {registered_year}")
    print("\n정부 공식 데이터를 조회합니다...")
    
    query = urllib.parse.quote(address_query.split('동 ')[0] if '동 ' in address_query else address_query.split('호')[0])
    vworld_key = "80194C85-0EE3-3220-A3C1-3268AD8756B9"
    vworld_url = f"http://api.vworld.kr/req/search?service=search&request=search&version=2.0&crs=EPSG:900913&size=10&page=1&query={query}&type=address&category=parcel&format=json&errorformat=json&key={vworld_key}"
    
    req = urllib.request.Request(vworld_url)
    req.add_header('Referer', 'http://localhost')
    res = urllib.request.urlopen(req)
    vworld_data = json.loads(res.read().decode('utf-8'))
    
    items = vworld_data.get('response', {}).get('result', {}).get('items', [])
    if not items:
        print("❌ VWorld에서 주소를 찾을 수 없어 조회를 중단합니다.")
        return
        
    pnu = items[0].get('id', '')
    sigunguCd, bjdongCd, bun, ji = pnu[0:5], pnu[5:10], pnu[11:15], pnu[15:19]
    
    bldg_data = get_building_data(sigunguCd, bjdongCd, bun, ji)
    expos_data = get_expos_data(sigunguCd, bjdongCd, bun, ji, dong_name, ho_name) if ho_name else None
    
    if not bldg_data:
        print("❌ 건축물대장 데이터를 불러오지 못했습니다.")
        return
        
    off_area = expos_data.get('area', '') if expos_data else bldg_data.get('totArea', '')
    off_floor = expos_data.get('flrNo', '') if expos_data else ''
    off_year = bldg_data.get('aprYear', '')
    
    print("\n==================================================")
    print(" 📊 매물 검증 리포트 (Audit Report)")
    print("==================================================")
    
    def check_match(name, reg_val, off_val):
        if not reg_val: reg_val = "입력안됨"
        if not off_val: off_val = "확인불가"
        
        # 숫자 비교를 위해 float 변환 시도
        try:
            reg_f = float(str(reg_val).replace(',', '').strip())
            off_f = float(str(off_val).replace(',', '').strip())
            match = (reg_f == off_f)
        except:
            # 글자 비교
            match = str(reg_val)[:4] == str(off_val)[:4] if name == '준공일' else str(reg_val) == str(off_val)
            
        status = "✅ 일치" if match else "🚨 불일치"
        print(f"[{status}] {name}")
        print(f"  - 화면 등록값: {reg_val}")
        print(f"  - 정부 공식값: {off_val}")
        print("-" * 50)
        
    check_match("전용면적", registered_area, off_area)
    if ho_name:
        check_match("해당 층수", registered_floor, off_floor)
    check_match("준공일", registered_year, off_year)
    
    print("📌 검증이 완료되었습니다. 화면 내용과 공식 데이터가 다를 경우 수정을 권장합니다.")
    input("\n엔터(Enter)를 치면 종료됩니다...")

if __name__ == "__main__":
    run_audit_lh()
