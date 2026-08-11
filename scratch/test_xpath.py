import os
from lxml import html as lxml_html

file_path = 'd:/부동산업무/antigravity/consult_diary/scratch/debug_serve.html'
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
except UnicodeDecodeError:
    with open(file_path, 'r', encoding='cp949', errors='ignore') as f:
        html = f.read()

tree = lxml_html.fromstring(html)

def check(xpath):
    elements = tree.xpath(xpath)
    print(f"XPath: {xpath} -> Found {len(elements)}")
    if elements:
        print(f"  First element tag: {elements[0].tag}, classes: {elements[0].get('class')}")

check("(//th[contains(., '주차대수')]/following-sibling::td//input)[1]")
check("(//th[contains(., '위반건축물')]/following-sibling::td//*[contains(@class, 'v-select') or contains(@class, 'select') or @role='combobox'])[1]")
check("(//th[contains(., '건축물용도')]/following-sibling::td//*[contains(@class, 'v-select') or contains(@class, 'select') or @role='combobox'])[1]")
check("(//th[contains(., '건축물일자')]/following-sibling::td//*[contains(@class, 'v-select') or contains(@class, 'select') or @role='combobox'])[1]")
check("//*[contains(@class, 'list-item') or contains(@class, 'menu') or @role='option']//*[contains(text(), '1997')]")

