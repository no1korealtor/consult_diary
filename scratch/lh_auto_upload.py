import time
import urllib.request
import urllib.parse
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from get_building_info import get_building_data, get_expos_data

def run_lh_auto_upload():
    print("==================================================")
    print("  LH 전세임대포털 매물 자동 등록 시스템 시작 ")
    print("==================================================")
    
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("detach", True)
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://jeonse.lh.or.kr")
        print("\n[2/3] 브라우저가 열렸습니다. 로그인을 진행해 주세요!")
        print("로그인 후, '신규 매물 등록' 화면으로 이동해 주세요.")
        
        while True:
            print("\n" + "="*50)
            print(" [새 매물 등록 대기 중] ")
            print(" 화면에서 주소를 검색하여 기본 세팅을 완료해 주세요.")
            user_input = input(" 입력을 다 하셨으면 엔터(Enter)를 치세요 (종료하려면 'q' 입력): ")
            
            if user_input.strip().lower() == 'q':
                print("\n수고하셨습니다! LH 자동 매물 등록 시스템을 종료합니다.")
                break
            
            # 화면에서 주소 읽어오기 (LH 폼)
            addr_val = ""
            detail_val = ""
            found = False
            
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                try:
                    addr_val = driver.find_element(By.ID, "rthousAddr").get_attribute("value")
                    detail_val = driver.find_element(By.ID, "detailAddr").get_attribute("value")
                    if addr_val: 
                        found = True
                        break
                except:
                    pass
                    
                frames = driver.find_elements(By.TAG_NAME, "iframe")
                for frame in frames:
                    try:
                        driver.switch_to.frame(frame)
                        addr_val = driver.find_element(By.ID, "rthousAddr").get_attribute("value")
                        detail_val = driver.find_element(By.ID, "detailAddr").get_attribute("value")
                        if addr_val:
                            found = True
                            break
                    except:
                        driver.switch_to.default_content()
                        
                if found:
                    break
                
            if not addr_val:
                print("\n❌ 앗! 현재 화면에서 주소 입력칸을 찾을 수 없습니다.")
                print("1. 혹시 '신규 매물 등록' 화면이 아닌 다른 화면에 계신 건 아닌가요?")
                print("2. 화면 로딩이 완전히 끝난 후 까만 창에서 엔터를 쳐주세요!")
                continue
                
            address_query = f"{addr_val} {detail_val}".strip()
            print(f"\n화면에서 주소 정보를 추출했습니다: {address_query}")
            
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
            
            query = urllib.parse.quote(address_query.split('동 ')[0] if '동 ' in address_query else address_query.split('호')[0])
            vworld_url = f"http://api.vworld.kr/req/search?service=search&request=search&version=2.0&crs=EPSG:900913&size=1&page=1&query={query}&type=address&category=parcel&format=json&errorformat=json&key=80194C85-0EE3-3220-A3C1-3268AD8756B9"
            
            print("\n[3/3] VWorld 및 정부 건축물대장 API 연동을 시작합니다...")
            req = urllib.request.Request(vworld_url)
            req.add_header('Referer', 'http://localhost')
            res = urllib.request.urlopen(req)
            vworld_data = json.loads(res.read().decode('utf-8'))
            
            items = vworld_data.get('response', {}).get('result', {}).get('items', [])
            if not items:
                print("❌ VWorld에서 주소를 찾을 수 없습니다.")
                continue
                
            pnu = items[0].get('id', '')
            sigunguCd = pnu[0:5]
            bjdongCd = pnu[5:10]
            bun = pnu[11:15]
            ji = pnu[15:19]
            
            print(f"✅ VWorld PNU 추출 완료: {pnu}")
            
            bldg_data = get_building_data(sigunguCd, bjdongCd, bun, ji)
            expos_data = get_expos_data(sigunguCd, bjdongCd, bun, ji, dong_name, ho_name) if ho_name else None
            
            if not bldg_data:
                print("❌ 건축물대장에서 데이터를 찾을 수 없습니다.")
                continue
                
            useAprDay = bldg_data.get('useAprDay', '')
            if not useAprDay and bldg_data.get('aprYear'):
                useAprDay = f"{bldg_data.get('aprYear')}{bldg_data.get('aprMonth')}{bldg_data.get('aprDay')}"
            
            if useAprDay and len(useAprDay) == 8:
                formatted_date = f"{useAprDay[:4]}-{useAprDay[4:6]}-{useAprDay[6:]}"
            else:
                formatted_date = useAprDay
                
            totArea = bldg_data.get('totArea', '')
            flrNo = expos_data.get('flrNo', '') if expos_data else ''
            area = expos_data.get('area', '') if expos_data else totArea
            supply_area = expos_data.get('supply_area', '') if expos_data else area
            if not supply_area:
                supply_area = area
            allFloor = bldg_data.get('grndFlrCnt', '')
            total_parking = bldg_data.get('totalParking', '0')
            households = bldg_data.get('households', '0')
            
            print(f"\n[건축물대장 정보 확인]")
            print(f"- 사용승인일: {formatted_date}")
            print(f"- 연면적: {totArea}㎡")
            print(f"- 층수: {flrNo}층 / 전체 {allFloor}층")
            print(f"- 전용면적: {area}㎡ / 공급면적: {supply_area}㎡")
            print(f"- 총주차대수: {total_parking}대 (가구수: {households})")
            
            try:
                # 1. 행정기관 승인기준 및 일자 입력
                try:
                    Select(driver.find_element(By.ID, "rthousAdmnstmachConfmStdr")).select_by_value("USE_CONFM_DE")
                except Exception as e:
                    print(f"  - 행정기관 승인기준 선택 실패: {e}")
                    
                try:
                    date_input = driver.find_element(By.ID, "rthousAdmnstmachConfmDe")
                    date_input.clear()
                    date_input.send_keys(formatted_date)
                except Exception as e:
                    print(f"  - 행정기관 승인일자 입력 실패: {e}")
                    
                # 2. 준공일 입력
                try:
                    compet_input = driver.find_element(By.ID, "rthousCompetDe")
                    compet_input.clear()
                    compet_input.send_keys(formatted_date)
                except Exception as e:
                    print(f"  - 준공일 입력 실패: {e}")
                    
                # 3. 면적 입력 (공급면적 / 전용면적)
                try:
                    hppr_input = driver.find_element(By.ID, "rthousHppr")
                    hppr_input.clear()
                    hppr_input.send_keys(str(supply_area))
                except Exception as e:
                    print(f"  - 공급면적 입력 실패: {e}")
                    
                try:
                    area_input = driver.find_element(By.ID, "rthousExclAr")
                    area_input.clear()
                    area_input.send_keys(str(area))
                except Exception as e:
                    print(f"  - 전용면적 입력 실패: {e}")
                    
                # 4. 층수 입력
                if flrNo:
                    flrNo_clean = str(flrNo).strip()
                    if flrNo_clean.startswith('-'):
                        try:
                            Select(driver.find_element(By.ID, "floorKind")).select_by_value("-")
                        except:
                            pass
                        flrNo_val = flrNo_clean.replace('-', '')
                    else:
                        try:
                            Select(driver.find_element(By.ID, "floorKind")).select_by_value("+")
                        except:
                            pass
                        flrNo_val = flrNo_clean
                        
                    try:
                        floor_input = driver.find_element(By.ID, "floor")
                        floor_input.clear()
                        floor_input.send_keys(str(flrNo_val))
                    except Exception as e:
                        print(f"  - 해당 층수 입력 실패: {e}")
                        
                # 5. 건물 전체 층수 입력
                if allFloor and allFloor != '0':
                    try:
                        all_floor_input = driver.find_element(By.ID, "rthousAllFloor")
                        all_floor_input.clear()
                        all_floor_input.send_keys(str(allFloor))
                    except Exception as e:
                        print(f"  - 건물 전체 층수 입력 실패: {e}")
                        
                # 6. 주차대수 입력
                try:
                    park_tot_input = driver.find_element(By.ID, "rthousParkngTotcnt")
                    park_tot_input.clear()
                    park_tot_input.send_keys(str(total_parking))
                except Exception as e:
                    print(f"  - 총 주차대수 입력 실패: {e}")
                    
                try:
                    park_cnt_input = driver.find_element(By.ID, "rthousParkngCnt")
                    park_cnt_input.clear()
                    try:
                        tot_p = float(total_parking)
                        hh = float(households)
                        if hh > 0:
                            per_hh = round(tot_p / hh, 2)
                            park_cnt_input.send_keys(str(per_hh))
                        else:
                            park_cnt_input.send_keys("0")
                    except:
                        park_cnt_input.send_keys("0")
                except Exception as e:
                    print(f"  - 가구당 주차대수 입력 실패: {e}")
                    
                print("\n 화면에 데이터 자동 입력이 완료되었습니다!")
                print("다음 매물을 위해 다시 주소를 입력하시고 엔터를 쳐주세요!")
            except Exception as e:
                print(f"\n⚠️ 화면에 데이터를 입력하는 중 오류가 발생했습니다: {e}")
                
    except Exception as e:
        print(f"에러가 발생했습니다: {e}")

if __name__ == "__main__":
    run_lh_auto_upload()
