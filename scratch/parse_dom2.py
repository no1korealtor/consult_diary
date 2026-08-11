import re

try:
    with open('d:/부동산업무/antigravity/consult_diary/scratch/debug_serve.html', 'r', encoding='utf-8') as f:
        html = f.read()
except:
    html = ''

targets = ['주차대수', '위반건축물', '건축물용도', '건축물일자']
for target in targets:
    print(f'\\n--- {target} ---')
    match = re.search(r'<th[^>]*>.*?'+target+r'.*?</th>\s*<td[^>]*>(.*?)</td>', html, re.IGNORECASE | re.DOTALL)
    if match:
        td = match.group(1)
        inputs = re.findall(r'<input([^>]+)>', td)
        for i, inp in enumerate(inputs):
            print(f'  Input {i}: {inp}')
            
        roles = re.findall(r'<div([^>]+role="combobox"[^>]*)>', td)
        for i, r in enumerate(roles):
            print(f'  Combobox {i}: {r}')
