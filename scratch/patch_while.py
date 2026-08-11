with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('while prop_type_name == "아파트" and apt_groups:', 'if prop_type_name == "아파트" and apt_groups:')

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(text)
