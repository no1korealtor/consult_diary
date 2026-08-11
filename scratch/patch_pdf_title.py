with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.strip().startswith("pdf_title = is_expanded and "):
        lines[i] = '        pdf_title = f"{masked_address} 인근 유사 매물 실거래 시세 브리핑" if is_expanded else f"{masked_address} 인근 실거래 시세 브리핑"\n'

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
