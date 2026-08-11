import os
import re

file_path = 'd:/부동산업무/antigravity/consult_diary/scratch/serve.html'
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
except UnicodeDecodeError:
    with open(file_path, 'r', encoding='cp949', errors='ignore') as f:
        html = f.read()

with open('test_output.txt', 'w', encoding='utf-8') as f:
    for lbl in ['총층', '총 주차대수', '위반건축물', '건축물용도', '건축물일자']:
        match = re.search(r'<th[^>]*>(.*?)'+lbl+r'(.*?)</th>', html, re.IGNORECASE | re.DOTALL)
        if match:
            f.write(f'{lbl}: MATCHED TH text: {match.group(0)}\n')
        else:
            f.write(f'{lbl}: TH NOT FOUND\n')
