with open('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('diff_parts.append("+", f"{""}{area_diff:.2f}㎡")', 'diff_parts.append(f"+{area_diff:.2f}㎡")')
content = content.replace('diff_parts.append("-", f"{""}{-area_diff:.2f}㎡")', 'diff_parts.append(f"{area_diff:.2f}㎡")')

with open('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)
