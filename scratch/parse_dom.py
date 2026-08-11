from bs4 import BeautifulSoup

try:
    with open('d:/부동산업무/antigravity/consult_diary/scratch/debug_serve.html', 'r', encoding='utf-8') as f:
        html = f.read()
except Exception as e:
    print('Failed to read:', e)
    html = ''

if html:
    soup = BeautifulSoup(html, 'html.parser')
    ths = soup.find_all('th')
    for th in ths:
        text = th.get_text(strip=True)
        if '주차대수' in text or '위반건축물' in text or '건축물용도' in text or '건축물일자' in text:
            print(f'\\nFound TH: {text}')
            td = th.find_next_sibling('td')
            inputs = td.find_all('input')
            for i, inp in enumerate(inputs):
                print(f'  Input {i}: type={inp.get("type")}, class={inp.get("class")}, disabled={inp.has_attr("disabled")}, readonly={inp.has_attr("readonly")}')
            
            selects = td.find_all(lambda tag: tag.has_attr('role') and tag['role'] == 'combobox')
            for i, sel in enumerate(selects):
                print(f'  Combobox {i}: tag={sel.name}, class={sel.get("class")}')
