import sys

with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('if target_floor is None:\n        floor_lbl = f"지하 {abs(target_floor)}층" if target_floor < 0 else f"{target_floor}층"', 'if target_floor is not None:\n        floor_lbl = f"지하 {abs(target_floor)}층" if target_floor < 0 else f"{target_floor}층"')

content = content.replace('if target_floor is None:\n                        floor_lbl = f"지하 {abs(target_floor)}층" if target_floor < 0 else f"{target_floor}층"', 'if target_floor is not None:\n                        floor_lbl = f"지하 {abs(target_floor)}층" if target_floor < 0 else f"{target_floor}층"')

content = content.replace('if target_floor is None:\n            fl = int(target_floor)', 'if target_floor is not None:\n            fl = int(target_floor)')

content = content.replace('if target_floor is not None or target_area is None:\n                                    if target_floor is None and floor is None:', 'if target_floor is not None and floor is not None:\n                                    if True:')

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed!')
