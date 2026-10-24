import re

with open('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern3 = re.compile(
    r'(\s+)floor = int\(floor_str\)\s+floor_display = f\"\{dong_prefix\}\{floor\}층\"'
)

replacement3 = r'''\1try:
\1    floor = int(floor_str)
\1    floor_display = f"{dong_prefix}{floor}층"
\1except:
\1    floor_display = f"{dong_prefix}{floor_str}층" if floor_str else dong_prefix.strip()'''

content = pattern3.sub(replacement3, content)

with open('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('d:/부동산업무/antigravity/consult_diary/scratch/test_trade_viewer.py', 'r', encoding='utf-8') as f:
    test_content = f.read()

test_content = test_content.replace('공공데이터 API 호출 오류 (인증 실패 / 403 Forbidden)', 'API 호출 오류 (인증 실패 / 403 Forbidden)')

with open('d:/부동산업무/antigravity/consult_diary/scratch/test_trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(test_content)
