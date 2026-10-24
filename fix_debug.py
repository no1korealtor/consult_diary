
with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('            target_label = get_size_category_label(target_area, prop_type_name, apt_groups) if target_area else \"\"', '            target_label = get_size_category_label(target_area, prop_type_name, apt_groups) if target_area else \"\"\\n            print(f\"DEBUG: target_area={target_area}, target_label={target_label}\")')

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)

