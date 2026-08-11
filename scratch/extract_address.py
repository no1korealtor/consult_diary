import time
from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options)
driver.get("https://www.serve.co.kr")

print("브라우저가 열렸습니다. 로그인 후 일반매물 등록 화면으로 가셔서,")
print("소재지(주소)와 본번, 부번(지번)을 입력해 주세요.")
input("다 입력하셨으면 엔터(Enter)를 치세요...")

try:
    sido = driver.find_element(By.XPATH, "//input[@aria-label='광역시도']/preceding-sibling::div/span").text
    sigungu = driver.find_element(By.XPATH, "//input[@aria-label='시/군/구']/preceding-sibling::div/span").text
    dong = driver.find_element(By.XPATH, "//input[@aria-label='읍/면/동']/preceding-sibling::div/span").text
    print(f"\n[성공] 추출된 주소: {sido} {sigungu} {dong}")
    
    # 본번 부번(번지) 찾기
    print("\n[번지 탐색]")
    inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
    bunji_found = False
    for inp in inputs:
        ph = inp.get_attribute("placeholder") or ""
        lbl = inp.get_attribute("aria-label") or ""
        val = inp.get_attribute("value") or ""
        
        # 값이 있는 text input 모두 출력 (디버깅 용)
        if val:
            print(f"발견된 입력값 - placeholder: '{ph}', aria-label: '{lbl}', value: '{val}'")
            
        # 12-1 이라는 placeholder를 가진 input이 번지 입력칸일 확률이 매우 높음
        if "12-1" in ph or "번지" in lbl or "번지" in ph:
            print(f"👉 [성공] 찾은 번지: {val}")
            bunji_found = True
            
        # 상세주소(호수) 입력칸 찾기
        if "예시" in ph or "동, 층, 호수" in ph or "상세" in lbl:
            if val:
                print(f"👉 [성공] 찾은 상세주소(호수): {val}")
            
    if not bunji_found:
        print("번지 입력칸을 찾지 못했습니다. 화면 구조가 예상과 다릅니다.")
except Exception as e:
    print(f"\n[오류] 주소 추출 실패: {e}")

input("\n확인하셨으면 창을 닫기 위해 엔터(Enter)를 치세요...")
driver.quit()
