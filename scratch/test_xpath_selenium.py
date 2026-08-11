from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os

file_path = os.path.abspath('debug_serve.html')

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

driver.get(f"file:///{file_path}")

def check(xpath):
    try:
        elements = driver.find_elements(By.XPATH, xpath)
        print(f"XPath: {xpath} -> Found {len(elements)}")
        if elements:
            el = elements[0]
            print(f"  First element tag: {el.tag_name}, classes: {el.get_attribute('class')}")
    except Exception as e:
        print(f"XPath failed: {e}")

check("(//th[contains(., '주차대수')]/following-sibling::td//input)[1]")
check("(//th[contains(., '위반건축물')]/following-sibling::td//*[contains(@class, 'v-select') or contains(@class, 'select') or @role='combobox'])[1]")
check("(//th[contains(., '건축물용도')]/following-sibling::td//*[contains(@class, 'v-select') or contains(@class, 'select') or @role='combobox'])[1]")
check("(//th[contains(., '건축물일자')]/following-sibling::td//*[contains(@class, 'v-select') or contains(@class, 'select') or @role='combobox'])[1]")

driver.quit()
