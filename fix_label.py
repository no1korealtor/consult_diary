
with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(' (유사 평형)', '')

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)

