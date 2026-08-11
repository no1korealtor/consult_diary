import time
import pyautogui
import pyperclip
import keyboard
import requests
import json
import urllib.request
import re

# API 키 설정
KAKAO_API_KEY = "133155e52871811db4337080ae0a2d13"
GOV_API_KEY = "88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770"

import sys
sys.stdout.reconfigure(line_buffering=True)

def get_kakao_address_info(address_str):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address_str}
    
    try:
        res = requests.get(url, headers=headers, params=params)
        data = res.json()
        if data.get("documents"):
            doc = data["documents"][0]
            addr = doc.get("address", {})
            if not addr: return None
            
            b_code = addr.get("b_code", "")
            if len(b_code) >= 10:
                return {
                    "sigunguCd": b_code[:5],
                    "bjdongCd": b_code[5:10],
                    "bun": addr.get("main_address_no", ""),
                    "ji": addr.get("sub_address_no", "0")
                }
    except Exception as e:
        print(f"카카오 API 에러: {e}")
    return None

def get_building_info(sigungu, bjdong, bun, ji):
    """표제부 (건물 전체 정보 - 단독/다가구/건물구조용)"""
    bun_str = str(bun).zfill(4) if bun else "0000"
    ji_str = str(ji).zfill(4) if ji else "0000"
    
    url = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo"
    query = f"?serviceKey={GOV_API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd=0&bun={bun_str}&ji={ji_str}&numOfRows=10&pageNo=1&_type=json"
    
    try:
        req = urllib.request.Request(url + query)
        req.add_header("User-Agent", "Mozilla/5.0")
        req.add_header("Accept", "application/json, text/plain, */*")
        with urllib.request.urlopen(req) as response:
            res_text = response.read().decode('utf-8')
            if not res_text.strip(): return None
            json_data = json.loads(res_text)
            items = json_data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            if not items: return None
            item = items[0]
            
            return {
                "platArea": str(item.get('platArea', 0)),
                "totArea": str(item.get('totArea', 0)),
                "purpose": item.get('mainPurpsCdNm', ""),
                "structure": item.get('strctCdNm', "")
            }
    except:
        return None

def get_expos_info(sigungu, bjdong, bun, ji, dong_name, ho_name):
    """전유부 (아파트 특정 호수 정보 - 전용면적용)"""
    url = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrExposPubuseAreaInfo"
    bun_str = str(bun).zfill(4) if bun else "0000"
    ji_str = str(ji).zfill(4) if ji else "0000"
    
    # 아파트는 platGbCd가 0(대지)일수도, 1(산)일수도, 2(블록)일수도 있지만 일단 0으로 시도
    for plat in [0, 1, 2]:
        query = f"?serviceKey={GOV_API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd={plat}&bun={bun_str}&ji={ji_str}&numOfRows=100&pageNo=1&_type=json"
        try:
            req = urllib.request.Request(url + query)
            req.add_header("User-Agent", "Mozilla/5.0")
            req.add_header("Accept", "application/json, text/plain, */*")
            res = urllib.request.urlopen(req)
            res_text = res.read().decode('utf-8')
            if not res_text.strip(): continue
            
            data = json.loads(res_text)
            items = data.get("response", {}).get("body", {}).get("items", {})
            if not items: continue
            
            item_list = items.get("item", [])
            if isinstance(item_list, dict): item_list = [item_list]
            
            area_exclusive = 0.0
            for item in item_list:
                api_dong = str(item.get('dongNm', ''))
                api_ho = str(item.get('hoNm', ''))
                
                # 동/호 매칭 (없거나 같으면 포함)
                match_dong = (not dong_name) or (dong_name in api_dong)
                match_ho = (not ho_name) or (ho_name in api_ho)
                
                if match_dong and match_ho:
                    # exposPubuseGbCd == '1' 이 전유부분
                    if str(item.get('exposPubuseGbCd', '')) == '1':
                        val = item.get('area')
                        if val: area_exclusive += float(val)
            
            if area_exclusive > 0:
                return {"area": str(round(area_exclusive, 2))}
        except:
            continue
    return None

def check_dagagu_ho_area(sigungu, bjdong, bun, ji):
    """다가구주택 호별면적 표시 여부 확인 (getBrExposPubuseAreaInfo 활용)"""
    url = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrExposPubuseAreaInfo"
    bun_str = str(bun).zfill(4) if bun else "0000"
    ji_str  = str(ji).zfill(4)  if ji  else "0000"

    for plat in [0, 1, 2]:
        query = (f"?serviceKey={GOV_API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}"
                 f"&platGbCd={plat}&bun={bun_str}&ji={ji_str}&numOfRows=100&pageNo=1&_type=json")
        try:
            req = urllib.request.Request(url + query)
            req.add_header("User-Agent", "Mozilla/5.0")
            req.add_header("Accept", "application/json, text/plain, */*")
            res = urllib.request.urlopen(req)
            res_text = res.read().decode('utf-8')
            if not res_text.strip(): continue

            data = json.loads(res_text)
            items = data.get("response", {}).get("body", {}).get("items", {})
            if not items: continue

            item_list = items.get("item", [])
            if isinstance(item_list, dict): item_list = [item_list]
            if not item_list: continue

            # 전유부(exposPubuseGbCd == '1') 데이터만 수집
            ho_list = []
            for item in item_list:
                if str(item.get('exposPubuseGbCd', '')) == '1':
                    ho_nm = item.get('hoNm', '-')
                    area  = item.get('area', 0)
                    ho_list.append((str(ho_nm), float(area) if area else 0.0))

            if ho_list:
                return ho_list  # [(호명, 면적), ...]
        except:
            continue
    return []  # 데이터 없음

def copy_field():
    pyperclip.copy("")
    pyautogui.press('end')
    time.sleep(0.05)
    pyautogui.hotkey('shift', 'home')
    time.sleep(0.05)
    pyautogui.keyDown('ctrl')
    time.sleep(0.05)
    pyautogui.press('c')
    time.sleep(0.05)
    pyautogui.keyUp('ctrl')
    time.sleep(0.1)
    return pyperclip.paste().strip()

def paste_field(text):
    if not text: return
    pyperclip.copy(text)
    pyautogui.keyDown('ctrl')
    time.sleep(0.05)
    pyautogui.press('v')
    time.sleep(0.05)
    pyautogui.keyUp('ctrl')
    time.sleep(0.1)

def fill_common_contract():
    """F4: 단독/다가구 모드"""
    print("\n" + "─"*50)
    print("[주의] 공공데이터 조회 결과는 참고용입니다.")
    print(" ※ 건축물대장(표제부)을 직접 발급받아 내용을 반드시 확인하세요!")
    print(" ※ 공적장부(건축물대장)가 기준이며, 공공데이터가 이를 대체하지 않습니다.")
    print("─"*50)
    print("[+] (단독/다가구 모드) 자동 완성을 시작합니다...")
    address = copy_field()
    print(f" -> 주소: {address}")
    
    addr_info = get_kakao_address_info(address)
    if not addr_info:
        print(" [!] 주소 변환 실패!")
        return
        
    bld_info = get_building_info(addr_info['sigunguCd'], addr_info['bjdongCd'], addr_info['bun'], addr_info['ji'])
    if not bld_info:
        print(" [!] 대장 정보 조회 실패!")
        return

    # ─── 다가구 호별면적 존재 여부 자동 확인 ───
    print(" ->\ 호별면적대장 조회 중...")
    ho_area_list = check_dagagu_ho_area(
        addr_info['sigunguCd'], addr_info['bjdongCd'], addr_info['bun'], addr_info['ji']
    )
    print("─"*50)
    if ho_area_list:
        print(" [확인] 이 건물은 호별면적 표시가 등록되어 있습니다!")
        print("   ※ 건축물대장 [호별면적대장]을 발급받아 확인하세요.")
        print(f"   (API 조회 기준 - {len(ho_area_list)}가구 전유부 데이터 존재)")
        for ho_nm, area in ho_area_list:
            print(f"     - {ho_nm}호 : {area} m2")
    else:
        print(" [확인] 호별면적 대장이 등록되어 있지 않습니다.")
        print("   (소유자가 표시변경을 신청하지 않았거나, 2018.12.4 이후 건충허가 건물이어도 해당 호의 데이터가 없는 경우)")
    print("─"*50)

    pyautogui.press('tab'); time.sleep(0.05) # 동 (스킵)
    
    # 호 칸 읽기: '*전부' 포함 여부로 전용면적 입력 여부 결정
    pyautogui.press('tab'); time.sleep(0.05) # 호
    ho_value = copy_field()
    is_jeonbu = "전부" in ho_value  # '전부', '*전부', '층 전부', '건물 전체' 등 포함 시
    print(f" -> 호 칸 값: '{ho_value}' / 전부 여부: {is_jeonbu}")
    
    pyautogui.press('tab'); time.sleep(0.05) # 지목
    paste_field("대")
    pyautogui.press('tab'); time.sleep(0.05) # 토지면적
    paste_field(bld_info['platArea'])
    pyautogui.press('tab'); time.sleep(0.05) # 구조
    paste_field(bld_info['structure'])
    pyautogui.press('tab'); time.sleep(0.05) # 용도
    paste_field(bld_info['purpose'])
    pyautogui.press('tab'); time.sleep(0.05) # 건물면적(전용면적)
    if is_jeonbu:
        # 건물 전체 또는 층 전체인 경우 → 면적 자동 입력
        paste_field(bld_info['totArea'])
        print(f" [+] 전용면적 입력: {bld_info['totArea']} (전부 해당)")
    else:
        # 일부인 경우 → 비워둠 (수기 입력 필요)
        print(" [+] 전용면적 비워둠 (일부 점유 - 수기 입력 필요)")
    print(" [+] 입력 완료!")

def fill_apartment_contract():
    """F5: 아파트/집합건물 모드"""
    print("\n" + "─"*50)
    print("[주의] 공공데이터 조회 결과는 참고용입니다.")
    print(" ※ 건축물대장(표제부 + 전유부)을 직접 발급받아 내용을 반드시 확인하세요!")
    print(" ※ 공적장부(건축물대장)가 기준이며, 공공데이터가 이를 대체하지 않습니다.")
    print("─"*50)
    print("[+] (아파트 모드) 자동 완성을 시작합니다...")
    # 0. 소재지
    address = copy_field()
    print(f" -> 주소: {address}")
    
    # 1. 동
    pyautogui.press('tab'); time.sleep(0.05)
    dong_name = copy_field()
    
    # 2. 호
    pyautogui.press('tab'); time.sleep(0.05)
    ho_name = copy_field()
    
    # 💡 동/호수 칸이 비어있으면 소재지(주소)에서 똑똑하게 찾아냄!
    if not dong_name:
        m = re.search(r'(\d+)[a-zA-Z가-힣]?동', address)
        if m: dong_name = m.group(1)
    if not ho_name:
        m = re.search(r'(\d+)[a-zA-Z가-힣]?호', address)
        if m: ho_name = m.group(1)
        
    print(f" -> 동: {dong_name}, 호: {ho_name}")
    
    addr_info = get_kakao_address_info(address)
    if not addr_info:
        print(" [!] 주소 변환 실패!")
        return
        
    # 구조, 용도, 토지면적을 얻기 위해 표제부 조회
    title_info = get_building_info(addr_info['sigunguCd'], addr_info['bjdongCd'], addr_info['bun'], addr_info['ji'])
    # 면적을 얻기 위해 전유부 조회
    expos_info = get_expos_info(addr_info['sigunguCd'], addr_info['bjdongCd'], addr_info['bun'], addr_info['ji'], dong_name, ho_name)
    
    if not title_info: title_info = {"structure": "", "purpose": "아파트", "platArea": ""}
    if not expos_info: expos_info = {"area": ""}
    
    print(f" -> 건물 정보: 대지면적({title_info['platArea']}), 구조({title_info['structure']}), 면적({expos_info['area']})")
    
    # 3. 지목 텍스트박스 (콤보박스는 탭으로 안 잡힘)
    pyautogui.press('tab'); time.sleep(0.05)
    paste_field("대")
    
    # 4. (대지권의 목적인 토지의 표시) 면적 -> 단지 전체 대지면적 기입
    pyautogui.press('tab'); time.sleep(0.05)
    paste_field(title_info['platArea'])

    # 5. 대지권종류 (스킵 - 수기입력)
    pyautogui.press('tab'); time.sleep(0.05)
    # 6. 대지권비율(분모) (스킵 - 수기입력)
    pyautogui.press('tab'); time.sleep(0.05)
    # 7. 대지권비율(분자) (스킵 - 수기입력)
    pyautogui.press('tab'); time.sleep(0.05)
    
    # 8. 건물구조
    pyautogui.press('tab'); time.sleep(0.05)
    paste_field(title_info['structure'])
    
    # 9. 용도
    pyautogui.press('tab'); time.sleep(0.05)
    paste_field(title_info['purpose'])
    
    # 10. 면적 (전용면적)
    pyautogui.press('tab'); time.sleep(0.05)
    paste_field(expos_info['area'])
    
    print(" [+] 아파트 입력 완료! (대지권 정보는 등기부등본 확인 후 수기입력)")

def check_building_register():
    """건축물대장 발급 여부 확인 및 공적장부 안내"""
    print("\n" + "═"*50)
    print("  [!] 건축물대장 확인 안내")
    print("═"*50)
    print("  이 프로그램은 공공데이터 API를 통해")
    print("  건물 정보(면적·구조·용도 등)를 자동으로 조회합니다.")
    print()
    print("  [!!]  [중요] 공적장부 확인 필수")
    print("  ─────────────────────────────────────────────")
    print("  공공데이터 조회 결과는 참고용 보조 수단이며,")
    print("  공적장부(건축물대장)를 법적으로 대체하지 않습니다.")
    print()
    print("  반드시 정부24 또는 세움터에서 건축물대장을")
    print("  직접 발급받아 내용을 검토한 후 광고를 게재하세요.")
    print("  ─────────────────────────────────────────────")
    print()

    # 단독/다가구
    print("  [단독·다가구·상가 매물]")
    print("   → 건축물대장 [표제부] 발급이 필요합니다.")
    print()
    print("  ※ 다가구주택 호별면적대장 추가 확인 안내")
    print("  ─────────────────────────────────────────────")
    print("  ■ 2018년 12월 4일 이후 건축허가 신청 다가구주택")
    print("    → 건축법 시행령 개정으로 가구별 전용면적이")
    print("      건축물대장에 의무적으로 기재됩니다.")
    print("    → [표제부 + 호별면적대장] 모두 발급받아 확인하세요.")
    print()
    print("  ■ 2018년 12월 4일 이전 건축허가 신청 다가구주택")
    print("    → 소유자가 관할 관청에 건축물대장 표시변경을")
    print("      신청한 경우, 호별 전용면적이 기재된")
    print("      호별면적대장이 존재할 수 있습니다.")
    print("    → 호별면적대장 발급 여부를 반드시 확인하세요!")
    print("  ─────────────────────────────────────────────")
    print()
    print("  [아파트·오피스텔·집합건물 매물]")
    print("   → 건축물대장 [표제부 + 전유부] 모두 발급이 필요합니다.")
    print()
    print("═"*50)

    while True:
        answer = input("  건축물대장을 모두 발급받으셨나요? (y / n): ").strip().lower()
        if answer == 'y':
            print("  [OK] 확인되었습니다. 자동 완성 봇을 시작합니다.\n")
            break
        elif answer == 'n':
            print()
            print("  [건축물대장 발급 방법]")
            print("   • 정부24: https://www.gov.kr (건축물대장 검색)")
            print("   • 세움터: https://cloud.eais.go.kr")
            print()
            print("  발급 후 다시 실행해 주세요. 프로그램을 종료합니다.")
            sys.exit(0)
        else:
            print("  y 또는 n 으로 입력해 주세요.")

def main():
    print("="*50)
    print("[+] 부동산 계약서 스마트 자동 완성 봇 대기 중 [+]")
    print(" - F4 키: [단독/다가구 모드] 자동 완성")
    print(" - F5 키: [아파트/오피스텔 모드] 자동 완성")
    print("\n사용법:")
    print(" 1. 한방 계약서의 '소재지' 칸을 클릭해 커서를 둡니다.")
    print("    (아파트의 경우 동, 호 칸에 값이 입력되어 있어야 전용면적을 정확히 가져옵니다!)")
    print(" 2. 양식에 맞게 F4 또는 F5 키를 누릅니다.")
    print(" 3. 마우스에서 손을 떼고 마법을 감상합니다.")
    print("="*50)

    # 건축물대장 발급 여부 확인
    check_building_register()
    
    keyboard.add_hotkey('f4', fill_common_contract)
    keyboard.add_hotkey('f5', fill_apartment_contract)
    keyboard.wait('esc')

if __name__ == "__main__":
    main()
