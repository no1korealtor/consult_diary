import re

try:
    with open('d:/부동산업무/antigravity/consult_diary/scratch/debug_serve.html', 'r', encoding='utf-8') as f:
        html = f.read()
except Exception as e:
    print('Failed to open file:', e)
    html = ''

if html:
    targets = ['주차대수', '위반건축물', '건축물용도', '건축물일자']
    for target in targets:
        print(f'\n--- {target} ---')
        match = re.search(r'<th[^>]*>.*?'+target+r'.*?</th>\s*<td[^>]*>(.*?)</td>', html, re.IGNORECASE | re.DOTALL)
        if match:
            td = match.group(1)
            print('Found inside TH.')
            print('Inputs:', len(re.findall(r'<input[^>]*>', td)))
            print('Select wrappers:', len(re.findall(r'<div[^>]*class="[^"]*v-select[^"]*"[^>]*>', td)))
            print('Text snippet:', td[:300].replace('\n', ' '))
        else:
            print('NOT FOUND in TH. Searching globally...')
            match2 = re.search(r'(.{0,100}'+target+r'.{0,300})', html, re.IGNORECASE | re.DOTALL)
            if match2:
                print('Global match snippet:', match2.group(1).replace('\n', ' '))
            else:
                print('Completely not found.')
