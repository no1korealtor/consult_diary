import time
from selenium import webdriver
from selenium.webdriver.common.by import By

def run_audit_prep():
    print("==================================================")
    print(" [매물 검증 봇(Audit Bot) 1단계] 화면 구조 스캔하기 ")
    print("==================================================")
    
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    
    driver.get("https://ma.serve.co.kr/good/articleRegistList") # 부동산써브 통합매물관리 목록
    
    print("\n[1] 크롬 창이 열렸습니다. 로그인을 진행해 주세요.")
    print("[2] 방금 캡처해서 보여주신 '통합매물관리 (매물 목록)' 화면으로 이동해 주세요.")
    print("[3] 여러 개의 매물이 화면에 보이면, 이 까만 창에서 엔터를 쳐주세요!")
    
    input("\n화면 이동이 끝났으면 엔터(Enter)를 치세요...")
    
    print("\n화면 구조를 스캔 중입니다...")
    
    # 팝업(새 창, iframe) 대응
    # 혹시 iframe 안에 매물 목록이 있을 수 있으니, 모든 프레임을 다 저장합니다.
    html_content = driver.page_source
    for frame in driver.find_elements(By.TAG_NAME, "iframe"):
        try:
            driver.switch_to.frame(frame)
            html_content += "\n\n<!-- IFRAME CONTENT -->\n\n" + driver.page_source
            driver.switch_to.default_content()
        except:
            pass
            
    # 현재 화면의 HTML 소스를 파일로 저장
    with open("serve_manage_list.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print("\n✅ 찰칵! 화면 구조 저장이 완료되었습니다!")
    print("이제 크롬 창은 닫으셔도 됩니다.")
    print("--------------------------------------------------")
    print("채팅창으로 돌아가셔서 저에게 '저장했어!' 라고 말씀해 주세요!")

if __name__ == "__main__":
    run_audit_prep()
