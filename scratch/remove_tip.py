import re
import os

path = r'd:\부동산업무\antigravity\consult_diary\deal-register.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'\s*<!-- 실무팁 배너 -->\s*<div id="tipBanner".*?</div>\s*<h3', '\n\n<h3', content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Replacement successful")
