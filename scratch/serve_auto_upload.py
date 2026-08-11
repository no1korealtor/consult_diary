import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import re
from get_building_info import get_building_data, get_expos_data, get_floor_data

_kept_alive_driver = None

def get_vworld_land_share(vworld_key, pnu, dong_name, ho_name):
    import urllib.request, json, re
    
    def match_part(target, item):
        if not target:
            return True
        if not item:
            return False
        t_str = str(target).strip().lower()
        i_str = str(item).strip().lower()
        if t_str == i_str:
            return True
        t_clean = t_str.replace('호', '').replace('동', '')
        i_clean = i_str.replace('호', '').replace('동', '')
        if t_clean == i_clean:
            return True
        t_num = re.sub(r'[^0-9]', '', t_clean)
        i_num = re.sub(r'[^0-9]', '', i_clean)
        if t_num and i_num:
            try:
                if int(t_num) == int(i_num):
                    return True
            except:
                pass
        return False

    url = f"http://api.vworld.kr/ned/data/ldaregList?key={vworld_key}&domain=http://localhost&pnu={pnu}&format=json&numOfRows=1000&pageNo=1"
    try:
        req = urllib.request.Request(url)
        req.add_header("Referer", "http://localhost")
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode('utf-8'))
        
        items = data.get('ldaregVOList', {}).get('ldaregVOList', [])
        if not items:
            # Fallback for new schema shape if it varies
            items = data.get('response', {}).get('ldaregVOList', [])
            
        for item in items:
            i_dong = str(item.get('buldDongNm', ''))
            i_ho = str(item.get('buldHoNm', ''))
            
            dong_match = match_part(dong_name, i_dong)
            ho_match = match_part(ho_name, i_ho)
            
            if dong_match and ho_match:
                rate = item.get('ldaQotaRate', '')
                if rate and '/' in rate:
                    return rate.split('/')[0].strip()
                return rate
    except Exception as e:
        print(f" -> [VWorld 에러] {e}")
    return ""

def select_transaction_type(driver, choice_str):
    xpaths = [
        f"//th[contains(., '거래 종류')]/following-sibling::td//label[contains(., '{choice_str}')]",
        f"//th[contains(., '거래 종류')]/following-sibling::td//*[contains(text(), '{choice_str}')]",
        f"//th[contains(., '거래 종류')]/following-sibling::td//span[contains(., '{choice_str}')]",
        f"//th[contains(., '거래 종류')]/following-sibling::td//input[@value='{choice_str}']"
    ]
    for xpath in xpaths:
        try:
            elements = driver.find_elements(By.XPATH, xpath)
            if elements:
                for el in elements:
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                        time.sleep(0.1)
                        try:
                            el.click()
                        except:
                            driver.execute_script("arguments[0].click();", el)
                        print(f" -> 거래 종류 [{choice_str}] 클릭 성공!")
                        return True
                    except:
                        continue
        except Exception:
            continue
    print(f" -> [경고] 거래 종류 [{choice_str}] 라디오 버튼을 자동 선택하지 못했습니다. 수동으로 선택해 주세요.")
    return False
def inject_preset_address(driver, preset_data):
    if not preset_data:
        return False
        
    sigungu_cd = preset_data.get("sigunguCd")
    bjdong_cd = preset_data.get("bjdongCd")
    sigungu_name = preset_data.get("sigungu_name")
    bjdong_name = preset_data.get("bjdong_name")
    bunji_val = preset_data.get("bunji_val")
    
    if not (sigungu_cd and bjdong_cd and sigungu_name and bjdong_name and bunji_val):
        return False
        
    try:
        sigungu_val = f"{sigungu_cd}00000|{sigungu_name}"
        dong_val = f"{sigungu_cd}{bjdong_cd}|{bjdong_name}"
        
        print(f"\n[주소 자동 입력 시작] {sigungu_name} {bjdong_name} {bunji_val}...")
        
        # 1. 시/군/구 입력
        sig_el = driver.find_element(By.XPATH, "//input[@aria-label='시/군/구']")
        driver.execute_script("arguments[0].value = arguments[1];", sig_el, sigungu_val)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", sig_el)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", sig_el)
        
        # 2. 읍/면/동 입력
        d_el = driver.find_element(By.XPATH, "//input[@aria-label='읍/면/동']")
        driver.execute_script("arguments[0].value = arguments[1];", d_el, dong_val)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", d_el)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", d_el)
        
        # 3. 번지 입력
        inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
        for inp in inputs:
            ph = inp.get_attribute("placeholder") or ""
            lbl = inp.get_attribute("aria-label") or ""
            if "12-1" in ph or "번지" in lbl or "번지" in ph:
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
                    time.sleep(0.1)
                    inp.click()
                    time.sleep(0.1)
                    inp.send_keys(Keys.CONTROL + "a")
                    inp.send_keys(Keys.BACKSPACE)
                    inp.send_keys(bunji_val)
                    driver.execute_script("""
                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    """, inp)
                    print(f" -> 번지 자동 입력 성공: {bunji_val}")
                except Exception as e_bunji:
                    driver.execute_script("arguments[0].value = arguments[1];", inp, bunji_val)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", inp)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", inp)
                    print(f" -> 번지 JS 강제 대입 성공: {bunji_val}")
                break
                
        # 4. hidden/ID 요소 입력
        for hid in ["sigunguCd", "bjdongCd", "mnnm", "slno"]:
            try:
                el = driver.find_element(By.ID, hid)
                if hid == "sigunguCd": val = sigungu_val
                elif hid == "bjdongCd": val = dong_val
                elif hid == "mnnm": val = bunji_val.split("-")[0] if "-" in bunji_val else bunji_val
                elif hid == "slno": val = bunji_val.split("-")[1] if "-" in bunji_val else ""
                
                driver.execute_script("arguments[0].value = arguments[1];", el, val)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", el)
                driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", el)
            except:
                pass
                
        # 5. 상세주소(동 호수) 입력
        ho_name = preset_data.get("ho_name") or ""
        dong_name_preset = preset_data.get("dong_name") or ""
        
        detail_val = ""
        if dong_name_preset and ho_name:
            ho_suffix = "호" if not ho_name.endswith("호") else ""
            dong_suffix = "동" if not dong_name_preset.endswith("동") else ""
            detail_val = f"{dong_name_preset}{dong_suffix} {ho_name}{ho_suffix}"
        elif ho_name:
            ho_suffix = "호" if not ho_name.endswith("호") else ""
            detail_val = f"{ho_name}{ho_suffix}"
            
        if detail_val:
            try:
                # refresh inputs to avoid stale element reference
                inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
                for inp in inputs:
                    ph = inp.get_attribute("placeholder") or ""
                    lbl = inp.get_attribute("aria-label") or ""
                    if "예시" in ph or "동, 층, 호수" in ph or "상세" in lbl:
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
                            time.sleep(0.1)
                            inp.click()
                            time.sleep(0.1)
                            inp.send_keys(Keys.CONTROL + "a")
                            inp.send_keys(Keys.BACKSPACE)
                            inp.send_keys(detail_val)
                            driver.execute_script("""
                                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                            """, inp)
                            print(f" -> 상세주소 자동 입력 완료: '{detail_val}'")
                        except Exception as e_detail_type:
                            driver.execute_script("arguments[0].value = arguments[1];", inp, detail_val)
                            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", inp)
                            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", inp)
                            print(f" -> 상세주소 JS 강제 대입 완료: '{detail_val}'")
                        break
            except Exception as ex_detail:
                print(f" -> [경고] 상세주소 자동 입력 중 오류: {ex_detail}")
                
        print(" -> 주소 자동 입력이 완료되었습니다!")
        return True
    except Exception as e:
        print(f" -> [경고] 주소 자동 입력 실패: {e}")
        return False

def run_serve_auto_upload(preset_data=None):
    global _kept_alive_driver
    preset_phone = preset_data.get('phone_number') if preset_data else None
    print("=" * 50)
    print(" 부동산써브 자동 매물 등록 시스템 시작 ")
    print("=" * 50)
    
    # 1. 크롬 브라우저 세팅
    print("\n[1/3] 크롬 브라우저를 확인합니다...")
    
    if _kept_alive_driver is not None:
        try:
            # 브라우저가 아직 켜져 있는지 확인
            _kept_alive_driver.current_url
            print(" -> 이미 열려있는 브라우저를 재사용합니다! (로그인 유지됨)")
        except Exception:
            _kept_alive_driver = None

    if _kept_alive_driver is None:
        print(" -> 새 브라우저를 엽니다...")
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_experimental_option("detach", True)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        _kept_alive_driver = webdriver.Chrome(options=options)
        _kept_alive_driver.get("https://www.serve.co.kr")
        print("\n[2/3] 브라우저가 열렸습니다. 로그인을 진행해 주세요!")
        print("로그인 후, 아파트가 아닌 **빌라, 상가, 단독주택** 등으로 매물 종류를 변경해 주세요.")
    else:
        print("\n[2/3] 기존 브라우저와 연결되었습니다! (이미 로그인되어 있다면 그대로 진행하세요)")
        print("새로운 매물 등록 화면에서 **빌라, 상가, 단독주택** 등으로 매물 종류를 선택해 주세요.")
        
    driver = _kept_alive_driver
    
    # 주소 자동 입력을 위한 preset 대기 및 처리
    if preset_data and preset_data.get("sigunguCd"):
        print("\n" + "="*70)
        print(" [자동 주소 입력 연동]")
        print(" 브라우저에서 로그인 후, 매물 등록 화면(빌라, 단독 등)으로 이동해 주세요.")
        print(" 이동 완료 후 콘솔창에서 엔터(Enter)를 누르면 주소와 번지가 자동 입력됩니다.")
        print("="*70)
        input(" -> 매물 등록 화면 이동 완료 시 엔터(Enter)를 눌러주세요... ")
        
        # 주소 주입 시도
        inject_preset_address(driver, preset_data)
    
    # 직전 성공 주소 캐시 (월세 전환 후 재입력 시 재사용)
    _last_addr_cache = {}

    try:
        while True:
            print("\n" + "="*50)
            print(" [1단계] 인터넷 창에서 소재지(주소)와 번지를 먼저 입력해 주세요.")
            print(" [2단계] 등록할 매물의 거래 종류를 번호로 선택해 주세요:")
            print("   1. 매매  |  2. 전세  |  3. 월세  |  4. 단기임대  (q: 메인 메뉴로)")
            print("="*50)
            
            if preset_data:
                trade_type = preset_data.get('trade_type')
                if not trade_type or trade_type == '임대차':
                    monthly_rent = preset_data.get('monthly_rent', 0)
                    if monthly_rent and int(monthly_rent) > 0:
                        trade_type = '월세'
                    else:
                        trade_type = '전세'
                        
                mapping = {'매매': '1', '전세': '2', '월세': '3'}
                user_input = mapping.get(trade_type, '1')
                print(f"\n [자동 연동] 거래 종류가 '{trade_type}'(으)로 자동 선택되었습니다.")
            else:
                user_input = input(" 선택 (1~4번, q: 취소) : ").strip()
                
            if user_input.lower() in ['q', 'ㅂ']:
                print("\n[안내] 입력을 취소하고 메인 메뉴로 돌아갑니다. (브라우저는 닫히지 않습니다)")
                return
                
            if user_input not in ['1', '2', '3', '4']:
                print("[오류] 잘못된 선택입니다. 1~4 사이의 번호를 입력해 주세요.")
                continue
            
            # ─── 가격 정보 추가 입력 받기 ───
            price_data = {}
            if user_input == '1':
                if preset_data and 'price' in preset_data:
                    price_data['매매가'] = str(preset_data['price'])
                    print(f" -> 매매가 자동 입력 설정: {price_data['매매가']} 만원")
                else:
                    val = input(" ▶ 매매가 입력 (만원 단위, 예: 5억 5천 -> 55000) : ").strip()
                    val = re.sub(r'[^\d]', '', val)
                    if val: price_data['매매가'] = val
            elif user_input == '2':
                if preset_data and 'price' in preset_data:
                    price_data['보증금'] = str(preset_data['price'])
                    print(f" -> 전세 보증금 자동 입력 설정: {price_data['보증금']} 만원")
                else:
                    val = input(" ▶ 전세 보증금 입력 (만원 단위, 예: 3억 -> 30000) : ").strip()
                    val = re.sub(r'[^\d]', '', val)
                    if val: price_data['보증금'] = val
            elif user_input in ['3', '4']:
                if preset_data and 'price' in preset_data:
                    price_data['보증금'] = str(preset_data['price'])
                    if 'monthly_rent' in preset_data:
                        price_data['월세'] = str(preset_data['monthly_rent'])
                    print(f" -> 보증금: {price_data.get('보증금')} 만원, 월세: {price_data.get('월세')} 만원 자동 입력 설정")
                else:
                    val_dep = input(" ▶ 보증금 입력 (만원 단위, 예: 2000) : ").strip()
                    val_dep = re.sub(r'[^\d]', '', val_dep)
                    val_rent = input(" ▶ 월세 입력 (만원 단위, 예: 60) : ").strip()
                    val_rent = re.sub(r'[^\d]', '', val_rent)
                    if val_dep: price_data['보증금'] = val_dep
                    if val_rent: price_data['월세'] = val_rent
            
            try:
                if preset_data and preset_data.get("sigunguCd"):
                    print("\n[자동 연동] 주소 정보를 preset_data에서 직접 추출합니다...")
                    sigunguCd = preset_data["sigunguCd"]
                    bjdongCd = preset_data["bjdongCd"]
                    bunji_val = preset_data["bunji_val"]
                    sigungu_name = preset_data["sigungu_name"]
                    bjdong_name = preset_data["bjdong_name"]
                    
                    sigungu_val = f"{sigunguCd}00000|{sigungu_name}"
                    dong_val = f"{sigunguCd}{bjdongCd}|{bjdong_name}"
                    
                    ho_name = preset_data.get("ho_name") or ""
                    dong_name_preset = preset_data.get("dong_name") or ""
                    if dong_name_preset and ho_name:
                        detail_val = f"{dong_name_preset}동 {ho_name}"
                    elif ho_name:
                        detail_val = f"{ho_name}"
                    else:
                        detail_val = ""
                else:
                    print("\n화면에서 주소 정보를 추출합니다...")
                
                    # 시군구 코드 추출
                    sigungu_val = driver.find_element(By.XPATH, "//input[@aria-label='시/군/구']").get_attribute("value")
                    sigunguCd = sigungu_val.split('|')[0][:5]
                
                    # 읍면동 코드 추출
                    dong_val = driver.find_element(By.XPATH, "//input[@aria-label='읍/면/동']").get_attribute("value")
                    bjdongCd = dong_val.split('|')[0][5:10]
                
                    # 번지 추출
                    bunji_val = ""
                    inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
                    for inp in inputs:
                        ph = inp.get_attribute("placeholder") or ""
                        lbl = inp.get_attribute("aria-label") or ""
                        if "12-1" in ph or "번지" in lbl or "번지" in ph:
                            bunji_val = inp.get_attribute("value") or ""
                            break
            
                # ✅ 번지 칸이 비어있을 때: 직전 성공 주소 재사용 (월세 전환 등으로 초기화된 경우 대응)
                if not bunji_val:
                    if _last_addr_cache:
                        print(f"\n[안내] 번지 칸이 비어있습니다. 직전에 입력한 주소({_last_addr_cache.get('bunji_val')})로 다시 시도합니다...")
                        sigunguCd = _last_addr_cache['sigunguCd']
                        bjdongCd  = _last_addr_cache['bjdongCd']
                        bunji_val = _last_addr_cache['bunji_val']
                    else:
                        print("\n[오류] 번지 입력을 찾지 못했습니다. 브라우저에서 번지 칸을 다시 채워주세요!")
                        continue
                
                bun = bunji_val.split("-")[0].zfill(4) if "-" in bunji_val else bunji_val.zfill(4)
                ji = bunji_val.split("-")[1].zfill(4) if "-" in bunji_val else "0000"
            
                # PNU 코드 조립
                pnu = f"{sigunguCd}{bjdongCd}1{bun}{ji}" # 1: 일반대지 (대부분의 경우)
                
                # ✅ 이번 주소 캐시 저장 (다음 루프에서 번지 칸이 초기화돼도 재사용 가능)
                _last_addr_cache = {'sigunguCd': sigunguCd, 'bjdongCd': bjdongCd, 'bunji_val': bunji_val}
            
                if not (preset_data and preset_data.get("sigunguCd")):
                    # 상세주소(호수) 추출
                    detail_val = ""
                    inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
                    for inp in inputs:
                        ph = inp.get_attribute("placeholder") or ""
                        lbl = inp.get_attribute("aria-label") or ""
                        if "예시" in ph or "동, 층, 호수" in ph or "상세" in lbl:
                            detail_val = inp.get_attribute("value") or ""
                            break
                        
                # ─── 거래 종류 자동 선택 ───
                deal_types = {
                    '1': '매매',
                    '2': '전세',
                    '3': '월세',
                    '4': '단기임대'
                }
                target_deal = deal_types[user_input]
                print(f"\n[거래종류 자동 클릭] 브라우저에서 '{target_deal}' 라디오 버튼을 선택합니다...")
                select_transaction_type(driver, target_deal)
                time.sleep(0.8)
                
                # ─── 주소 자동 복구 (거래종류 변경 시 초기화되는 경우 대비) ───
                try:
                    sigungu_check = driver.find_element(By.XPATH, "//input[@aria-label='시/군/구']").get_attribute("value")
                    if not sigungu_check:
                        print(" -> [알림] 거래 종류 변경으로 주소가 초기화되었습니다. 주소를 자동으로 복구합니다...")
                        
                        # 1. 시/군/구 복구
                        sig_el = driver.find_element(By.XPATH, "//input[@aria-label='시/군/구']")
                        driver.execute_script("arguments[0].value = arguments[1];", sig_el, sigungu_val)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", sig_el)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", sig_el)
                        
                        # 2. 읍/면/동 복구
                        d_el = driver.find_element(By.XPATH, "//input[@aria-label='읍/면/동']")
                        driver.execute_script("arguments[0].value = arguments[1];", d_el, dong_val)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", d_el)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", d_el)
                        
                        # 3. 번지 및 상세주소 복구
                        inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
                        for inp in inputs:
                            ph = inp.get_attribute("placeholder") or ""
                            lbl = inp.get_attribute("aria-label") or ""
                            if "12-1" in ph or "번지" in lbl or "번지" in ph:
                                driver.execute_script("arguments[0].value = arguments[1];", inp, bunji_val)
                                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", inp)
                                driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", inp)
                            elif "예시" in ph or "동, 층, 호수" in ph or "상세" in lbl:
                                driver.execute_script("arguments[0].value = arguments[1];", inp, detail_val)
                                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", inp)
                                driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", inp)
                                
                        # 4. hidden/ID 요소 복구 (존재 시)
                        for hid in ["sigunguCd", "bjdongCd", "mnnm", "slno"]:
                            try:
                                el = driver.find_element(By.ID, hid)
                                if hid == "sigunguCd": val = sigungu_val
                                elif hid == "bjdongCd": val = dong_val
                                elif hid == "mnnm": val = bunji_val.split("-")[0] if "-" in bunji_val else bunji_val
                                elif hid == "slno": val = bunji_val.split("-")[1] if "-" in bunji_val else ""
                                
                                driver.execute_script("arguments[0].value = arguments[1];", el, val)
                                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", el)
                                driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", el)
                            except:
                                pass
                                
                        print(" -> 주소 자동 복구가 완료되었습니다!")
                except Exception as restore_err:
                    print(f" -> [경고] 주소 복구 중 오류 발생: {restore_err}")
                
                dong_name = ""
                ho_name = ""
                if detail_val:
                    dong_match = re.search(r'([0-9가-힣]+)동', detail_val)
                    # '호'가 명시적으로 있으면 그 앞의 숫자, 없으면 문자열 내의 마지막 숫자 뭉치를 호수로 간주
                    ho_match = re.search(r'([0-9]+)호', detail_val)
                    if not ho_match:
                        nums = re.findall(r'([0-9]+)', detail_val)
                        if nums:
                            ho_name = nums[-1] # 보통 맨 끝 숫자가 호수
                    else:
                        ho_name = ho_match.group(1)
                
                    if dong_match: dong_name = dong_match.group(1)
            
                is_entire_floor = False
                floor_name = ""
                if "전부" in detail_val or "전체" in detail_val:
                    is_entire_floor = True
                    flr_match = re.search(r'(지하\s*)?([0-9]+)층', detail_val)
                    if flr_match:
                        floor_name = flr_match.group(0).replace(" ", "")
                    ho_name = "" # 전체 층이므로 호수는 없음
                    print(f" -> 추출된 상세주소: '{detail_val}' => [전체 층 임대] 동: '{dong_name}', 층: '{floor_name}'")
                else:
                    print(f" -> 추출된 상세주소: '{detail_val}' => 동: '{dong_name}', 호: '{ho_name}'")
            
                print(f" -> 추출된 법정동코드: {sigunguCd}{bjdongCd}, 번지: {bun}-{ji}")
        
                print("\n[VWorld] 대지권등록부에서 대지지분을 자동 조회합니다...")
                vworld_key = "80194C85-0EE3-3220-A3C1-3268AD8756B9"
                auto_land_share = get_vworld_land_share(vworld_key, pnu, dong_name, ho_name)
        
                if auto_land_share:
                    print(f" -> [대지지분 조회 성공!] {auto_land_share} ㎡")
                    land_share = auto_land_share
                else:
                    print(" -> 대지지분 조회 실패 (또는 단독주택). 대지지분 입력을 건너뜁니다.")
                    land_share = ""
        
                # 2. API 데이터 조회
                print("\n[3/3] 공공데이터에서 건축물대장 정보를 조회합니다...")

                data = get_building_data(sigunguCd, bjdongCd, bun, ji)
        
                if is_entire_floor and floor_name:
                    expos_data = get_floor_data(sigunguCd, bjdongCd, bun, ji, floor_name)
                elif ho_name:
                    expos_data = get_expos_data(sigunguCd, bjdongCd, bun, ji, dong_name, ho_name)
                else:
                    expos_data = None

                if not data:
                    print("\n[오류] 정부 서버에서 건축물대장 데이터를 찾을 수 없습니다.")
                    print("브라우저에서 입력하신 '번지'가 정확한지 확인하시고 수정하신 뒤 다시 엔터를 쳐주세요!")
                    continue

                print(f" -> 성공! 연면적: {data['totArea']}㎡, 총주차: {data['totalParking']}대, 승인년도: {data['aprYear']}년")
                if expos_data:
                    if is_entire_floor:
                        print(f" -> [층별개요 성공!] {dong_name}동 {floor_name} 면적: {expos_data.get('area')}㎡ (공급/전용 동일)")
                    else:
                        print(f" -> [전유부 성공!] {dong_name}동 {ho_name}호 전용면적: {expos_data.get('area')}㎡, 층: {expos_data.get('flrNo')}층")

                # ─── 다가구주택 호별면적 표시 여부 자동 확인 ───
                print("\n[호별면적] 다가구주택 호별면적 등록 여부를 확인합니다...")
                try:
                    import urllib.request as _ureq, json as _json
                    _gov_key = "88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770"
                    _url = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrExposPubuseAreaInfo"
                    _bun4 = str(bun).zfill(4)
                    _ji4  = str(ji).zfill(4)
                    _ho_list = []
                    for _plat in [0, 1, 2]:
                        _q = (f"?serviceKey={_gov_key}&sigunguCd={sigunguCd}&bjdongCd={bjdongCd}"
                              f"&platGbCd={_plat}&bun={_bun4}&ji={_ji4}&numOfRows=100&pageNo=1&_type=json")
                        try:
                            _req = _ureq.Request(_url + _q)
                            _req.add_header("User-Agent", "Mozilla/5.0")
                            _req.add_header("Accept", "application/json, text/plain, */*")
                            _res = _ureq.urlopen(_req)
                            _txt = _res.read().decode('utf-8')
                            if not _txt.strip(): continue
                            _d = _json.loads(_txt)
                            _items = _d.get("response", {}).get("body", {}).get("items", {})
                            if not _items: continue
                            _item_list = _items.get("item", [])
                            if isinstance(_item_list, dict): _item_list = [_item_list]
                            for _item in _item_list:
                                if str(_item.get('exposPubuseGbCd', '')) == '1':
                                    _ho_list.append((str(_item.get('hoNm', '-')),
                                                     float(_item.get('area', 0) or 0)))
                            if _ho_list: break
                        except:
                            continue

                    print("─" * 50)
                    if _ho_list:
                        print(f" [확인] 이 건물은 호별면적 표시가 등록되어 있습니다! ({len(_ho_list)}가구)")
                        print("   ※ 건축물대장 [호별면적대장]을 발급받아 광고 면적을 확인하세요.")
                        for _ho_nm, _area in _ho_list:
                            print(f"     - {_ho_nm}호 : {_area} m2")
                    else:
                        print(" [확인] 호별면적 대장이 등록되어 있지 않습니다.")
                        print("   (소유자가 표시변경을 신청하지 않았거나, 해당 호의 데이터가 없는 경우)")
                    print("─" * 50)
                except Exception as _e:
                    print(f" [호별면적 조회 오류] {_e}")

                print("\n화면에서 입력칸을 찾아 자동 입력을 시작합니다...")
        
                # 디버깅용 HTML 저장
                try:
                    with open('debug_serve.html', 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                except:
                    pass
            
                time.sleep(1)
        
                # -----------------------------------------------------
                # 화면의 요소(ID나 Name)를 찾아서 자동으로 값을 밀어넣는 코드들
                # (Vuetify 등 동적 ID를 사용하는 최신 웹사이트용 XPath 방식)
                # -----------------------------------------------------
                def enter_value(label_texts, value, input_index=1):
                    if not value: return
                    if isinstance(label_texts, str): label_texts = [label_texts]
                    for label_text in label_texts:
                        xpath = f"(//th[contains(., '{label_text}')]/following-sibling::td//input[not(@type='hidden') and not(@type='radio') and not(@type='checkbox')])"
                        inputs = driver.find_elements(By.XPATH, xpath)
                
                        # If a specific input_index is provided (e.g. for ground/underground floors), we slice the list
                        if input_index > 1:
                            inputs = inputs[input_index - 1:]
                    
                        for el in inputs:
                            try:
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                                time.sleep(0.1)
                                try:
                                    ActionChains(driver).move_to_element(el).click().perform()
                                except:
                                    driver.execute_script("arguments[0].click();", el)
                                time.sleep(0.1)
                        
                                el.send_keys(Keys.CONTROL + "a")
                                el.send_keys(Keys.BACKSPACE)
                                el.send_keys(str(value))

                                # Vue/React 등 동적 프레임워크 상태 업데이트를 위한 강제 이벤트 발생
                                driver.execute_script("""
                                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                                """, el)
                        
                                print(f" -> [{label_texts[0]}] '{value}' 자동 입력 완료!")
                                return # 성공하면 즉시 리턴
                            except Exception as inner_e:
                                continue
                    print(f" -> [X] [{label_texts[0]}] 텍스트 입력칸을 찾지 못했거나 입력에 실패했습니다.")

                def select_vuetify_dropdown(label_texts, option_text, dropdown_index=1):
                    if not option_text: return
                    if isinstance(label_texts, str): label_texts = [label_texts]
                    for label_text in label_texts:
                        try:
                            # target the input inside the combobox (라디오 버튼 제외!)
                            xpath = f"(//th[contains(., '{label_text}')]/following-sibling::td//input[not(@type='hidden') and not(@type='radio') and not(@type='checkbox')])[{dropdown_index}]"
                            triggers = driver.find_elements(By.XPATH, xpath)
                            if not triggers:
                                # fallback to combobox role
                                xpath2 = f"(//th[contains(., '{label_text}')]/following-sibling::td//*[@role='combobox'])[{dropdown_index}]"
                                triggers = driver.find_elements(By.XPATH, xpath2)
                                if not triggers: continue
                        
                            trigger = triggers[0]
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", trigger)
                            time.sleep(0.1)
                    
                            try:
                                trigger.click()
                            except:
                                driver.execute_script("arguments[0].click();", trigger)
                    
                            time.sleep(0.2)
                            try:
                                trigger.send_keys(Keys.ARROW_DOWN)
                            except:
                                pass
                            time.sleep(0.5)
                    
                            # 옵션 텍스트 정확히 매칭 (substring 매칭으로 인한 오동작 방지)
                            option_text_no_space = option_text.replace(" ", "")
                            option_text_short = option_text_no_space[:4] if len(option_text_no_space) > 4 else option_text_no_space
                    
                            exact_matches = [
                                f"normalize-space(.)='{option_text}'",
                                f"normalize-space(.)='0{option_text}'",
                                f"normalize-space(.)='{option_text}년'",
                                f"normalize-space(.)='{option_text}월'",
                                f"normalize-space(.)='0{option_text}월'",
                                f"normalize-space(.)='{option_text}일'",
                                f"normalize-space(.)='0{option_text}일'"
                            ]
                    
                            # 숫자(월, 일)일 때는 contains를 쓰면 이전 드롭다운의 잔여물(예: 1996년)과 충돌하므로 긴 문자열(용도 등)에만 허용
                            if len(option_text_no_space) > 2:
                                exact_matches.append(f"contains(translate(., ' ', ''), '{option_text_no_space}')")
                                exact_matches.append(f"contains(translate(., ' ', ''), '{option_text_short}')")
                        
                            match_condition = " or ".join(exact_matches)
                    
                            # 반드시 드롭다운 팝업(v-overlay-container) 내에서만 찾도록 제한하여 화면의 정적 텍스트를 클릭하는 버그 원천 차단!
                            option_xpath = f"//div[contains(@class, 'v-overlay-container')]//*[contains(@class, 'v-list-item') or @role='option'][.//text()[{match_condition}]]"
                    
                            # 반드시 보여질 때까지 대기! (안 열렸으면 여기서 에러 남)
                            try:
                                # 여러 개가 찾아질 수 있으므로, visible 한 것 중 첫 번째 것을 선택
                                options = WebDriverWait(driver, 1.5).until(EC.visibility_of_all_elements_located((By.XPATH, option_xpath)))
                                option = options[-1] # 보통 마지막에 열린 메뉴가 가장 하단(DOM 끝)에 추가됨
                        
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option)
                                time.sleep(0.1)
                        
                                try:
                                    ActionChains(driver).move_to_element(option).click().perform()
                                except:
                                    driver.execute_script("arguments[0].click();", option)
                                time.sleep(0.3)
                                return
                            except Exception as inner_e:
                                # 옵션을 못 찾아서 실패했을 경우, 열려있는 드롭다운 메뉴를 ESC로 닫아주어야 다음 요소 클릭이 가능함
                                try:
                                    trigger.send_keys(Keys.ESCAPE)
                                except:
                                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                                time.sleep(0.2)
                                raise inner_e
                        except Exception as e:
                            pass
                    print(f"[{label_texts[0]}] 드롭다운 '{option_text}' 선택 실패.")

                # [가격 정보 입력]
                if '매매가' in price_data:
                    enter_value("매매가", price_data['매매가'])
                if '보증금' in price_data:
                    enter_value("보증금", price_data['보증금'])
                if '월세' in price_data:
                    enter_value("월세", price_data['월세'])

                # [전용면적, 공급면적, 연면적, 대지면적, 건축면적]
                if expos_data:
                    enter_value("전용면적", expos_data.get('area', ''))
                    enter_value("공급면적", expos_data.get('supply_area', ''))
            
                enter_value("연면적", data.get('totArea', ''))
                enter_value("대지면적", data.get('platArea', ''))
                enter_value("건축면적", data.get('archArea', ''))
        
                # [대지지분]
                if land_share:
                    enter_value(["대지지분", "지분"], land_share)
        
        
                # [층수 입력 (집합건물 vs 단독/다가구 로직 분리 및 건물일부 vs 건물전체 대응)]
                has_haedang_flr = len(driver.find_elements(By.XPATH, "//th[contains(., '해당층')]")) > 0
                
                if has_haedang_flr:
                    # 건물 일부 (방 또는 일부) 등록 시: 해당층과 해당동 총층을 입력
                    tot_flr = data.get('grndFlrCnt', '')
                    cur_flr = ''
                    if expos_data and expos_data.get('flrNo'):
                        cur_flr = str(expos_data.get('flrNo'))
                    else:
                        # 호수(ho_name)나 상세주소(detail_val)로부터 층수 추정
                        flr_match = re.search(r'(지하\s*)?([0-9]+)층', detail_val)
                        if flr_match:
                            cur_flr = flr_match.group(2)
                            if flr_match.group(1):
                                cur_flr = "-" + cur_flr
                        elif ho_name:
                            ho_clean = re.sub(r'[^\d]', '', ho_name)
                            if ho_clean.isdigit():
                                if len(ho_clean) >= 3:
                                    cur_flr = ho_clean[:-2]
                                elif len(ho_clean) > 0:
                                    cur_flr = ho_clean
                            if "지하" in ho_name or "B" in ho_name.upper():
                                digits = re.findall(r'\d+', ho_name)
                                if digits:
                                    d_val = digits[0]
                                    if len(d_val) >= 3:
                                        cur_flr = "-" + d_val[:-2]
                                    else:
                                        cur_flr = "-" + d_val
                                else:
                                    cur_flr = "-1"
                    try:
                        if cur_flr and tot_flr and int(cur_flr) > int(tot_flr):
                            print(f"\n[주의] 해당층({cur_flr}층) > 총층({tot_flr}층) — 공부상 층수 불일치!")
                            print("   표제부 지상층수와 실제 층수가 다를 수 있습니다. 건축물대장을 직접 확인하세요.")
                            print("   해당층은 입력하지 않고 비워둡니다. (수기 입력 필요)")
                            cur_flr = ''
                    except (ValueError, TypeError):
                        pass
                    enter_value(["해당층"], cur_flr, 1)
                    enter_value(["총층"], tot_flr, 2)
                else:
                    # 건물 전체 등록 시 (지상/지하층 입력 칸)
                    enter_value(['총층', '층수', '지상'], data.get('grndFlrCnt', ''), 1)
                    enter_value(['총층', '층수', '지하'], data.get('ugrndFlrCnt', ''), 2)
        
                # [세대수 / 가구수]
                enter_value(["세대", "가구"], data.get('households', ''))
        
                # [주차가능여부 및 총 주차대수]
                try:
                    if data.get('canPark') == 'Y':
                        park_radio = driver.find_element(By.XPATH, "//th[contains(., '주차가능여부')]/following-sibling::td//input[@value='Y' or contains(@value, '1')]")
                        driver.execute_script("arguments[0].click();", park_radio)
                except:
                    pass
                enter_value(["총 주차대수", "주차대수"], data.get('totalParking', ''))
        
                # [위반건축물여부]
                # 표제부에서 확인
                is_violation = (data.get('violBldYn') == 'Y') or (data.get('vlratEstmTotArea', 0) > 0)
        
                # 전유부(상세주소) 정보가 있다면 전유부를 최우선 기준으로 덮어쓰기!
                if expos_data:
                    if expos_data.get('violBldYn') == 'Y':
                        is_violation = True
                    else:
                        is_violation = False
                
                v_text = "예" if is_violation else "아니오"
                select_vuetify_dropdown(["위반건축물", "위반"], v_text)
        
                # [건축물용도] 
                main_purps = data.get('purpose', '').strip()
                if main_purps:
                    select_vuetify_dropdown(["용도", "건축물용도"], main_purps)
                else:
                    print("[알림] 정부 데이터에 '건축물용도' 값이 없어서 입력을 건너뜁니다.")
            
                # [건축물일자 (사용승인일)]
                year = data.get('aprYear', '')
                month = data.get('aprMonth', '')
                day = data.get('aprDay', '')
        
                if year and month and day:
                    # "06" -> "6", "01" -> "1"
                    month_str = str(int(month))
                    day_str = str(int(day))
            
                    # 첫 번째 드롭다운 (기준: 사용승인일/착공일)
                    select_vuetify_dropdown(["일자", "건축물일자"], "사용승인일", 1)
                    # 년/월/일
                    select_vuetify_dropdown(["일자", "건축물일자"], year, 2)
                    select_vuetify_dropdown(["일자", "건축물일자"], month_str, 3)
                    select_vuetify_dropdown(["일자", "건축물일자"], day_str, 4)
                else:
                    print(f"[알림] 정부 데이터의 '사용승인일' 값이 유효하지 않아 입력을 건너뜁니다.")
        
                # [의뢰인 연락처 자동 입력]
                if preset_phone:
                    print(f"\n[의뢰인 연락처 자동 입력] 의뢰인 연락처 입력을 시도합니다 ({preset_phone})...")
                    enter_value(["의뢰인연락처", "소유자연락처", "의뢰인 연락처", "소유자 연락처", "연락처", "전화번호", "소유주연락처"], preset_phone)
        
                print("\n[성공] 필수 데이터들을 자동으로 채워 넣었습니다!")
                print("인터넷 창은 그대로 열어둘 테니, 나머지 정보(금액, 사진 등)를 천천히 입력하시고 '매물 등록' 버튼을 직접 눌러주세요!")
            
                # 1회 자동 입력을 완료했으므로 preset_data를 비워 다음 루프부터는 수동 선택 대기하도록 함
                preset_data = None
            
                user_input = input("\n[안내] 주소를 잘못 쳤거나, 이어서 다음 매물을 하려면 인터넷 창에서 주소를 입력 후 다시 엔터(Enter)를 치세요! (메뉴로 나가기: q) : ")
                if user_input.strip().lower() in ['q', 'ㅂ']:
                    print("\n메인 메뉴로 돌아갑니다...")
                    return
                else:
                    print("\n[안내] 이 창에서 계속해서 자동 입력을 대기합니다.")
                    continue
            
            except Exception as e:
                # 에러 발생 시에도 다음 시도를 위해 preset_data 비움
                preset_data = None
                error_msg = str(e).split('Stacktrace:')[0].strip()
                print(f"\n[오류] 주소 정보를 추출할 수 없거나 처리 중 문제가 발생했습니다.")
                print(f"상세 내용: {error_msg}")
                print("주소를 끝까지 선택하셨는지, 아직 로딩 중은 아닌지 확인하시고 다시 엔터를 쳐주세요!")
                continue
        
    except Exception as e:
        print(f"매크로 작동 중 오류: {e}")
        input("\n[오류] 확인을 위해 엔터를 치면 메뉴로 돌아갑니다...")

if __name__ == "__main__":
    run_serve_auto_upload()
