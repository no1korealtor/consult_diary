import time
import urllib.request
import urllib.parse
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By

from get_building_info import get_building_data, get_expos_data

def run_audit_serve():
    print("==================================================")
    print(" 🕵️‍♂️ 부동산써브 매물 자동 검증 봇 (Audit Bot) 실행 ")
    print("==================================================")
    
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    
    driver.get("https://www.serve.co.kr")
    
    print("\n[1] 크롬 창이 열렸습니다. 로그인을 진행해 주세요.")
    
    while True:
        print("\n" + "="*50)
        print(" [검증 대기 중] ")
        print(" 방금 올리셨거나 광고 중인 매물의 '수정(또는 상세)' 화면으로 이동해 주세요.")
        print(" (주소, 면적, 층수 등이 입력칸에 보이는 화면이어야 합니다)")
        user_input = input(" 화면 이동이 끝났으면 엔터(Enter)를 치세요 (종료하려면 'q' 입력): ")
        
        if user_input.strip().lower() == 'q':
            print("\n수고하셨습니다! 부동산써브 검증 봇을 종료합니다.")
            break
            
        print("\n화면에서 매물 정보를 훔쳐(?)오는 중입니다...")
        
        try:
            # 주소 정보 (부동산써브는 코드가 바로 있음)
            sigungu_val = driver.find_element(By.ID, "sigunguCd").get_attribute("value")
            dong_val = driver.find_element(By.ID, "bjdongCd").get_attribute("value")
            bun = driver.find_element(By.ID, "mnnm").get_attribute("value")
            ji = driver.find_element(By.ID, "slno").get_attribute("value")
            
            sigunguCd = sigungu_val.split('|')[0][:5]
            bjdongCd = dong_val.split('|')[0][5:10]
            
            # 동호수 (있는 경우)
            dong_name = driver.find_element(By.ID, "dongNm").get_attribute("value").replace("동", "")
            ho_name = driver.find_element(By.ID, "hoNm").get_attribute("value").replace("호", "")
            
            # 화면에 등록된 값 추출
            registered_area = driver.find_element(By.ID, "exclAr").get_attribute("value")
            registered_floor = driver.find_element(By.ID, "flrNo").get_attribute("value")
            registered_year = driver.find_element(By.ID, "usoConfmYear").get_attribute("value")
            
            print(f"✅ 화면 정보 파싱 완료!")
            
        except Exception as e:
            print("❌ 정보를 찾을 수 없습니다. '매물 수정' 화면이 맞는지 확인해주세요!")
            continue
            
        print("\n정부 공식 데이터를 조회합니다...")
        
        bldg_data = get_building_data(sigunguCd, bjdongCd, bun, ji)
        expos_data = get_expos_data(sigunguCd, bjdongCd, bun, ji, dong_name, ho_name) if ho_name else None
        
        if not bldg_data:
            print("❌ 건축물대장 데이터를 불러오지 못했습니다. 주소를 다시 확인해주세요.")
            continue
            
        off_area = expos_data.get('area', '') if expos_data else bldg_data.get('totArea', '')
        off_floor = expos_data.get('flrNo', '') if expos_data else ''
        off_year = bldg_data.get('aprYear', '')
        
        print("\n==================================================")
        print(" 📊 부동산써브 매물 검증 리포트 (Audit Report)")
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
        
        print("📌 검증이 완료되었습니다. 다른 매물을 검증하시려면 사이트에서 다른 매물의 '수정' 창을 띄우고 다시 엔터를 치세요!")

if __name__ == "__main__":
    run_audit_serve()
