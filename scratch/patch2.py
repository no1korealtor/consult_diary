with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "amt = dep + mon * 100" in line:
        # Before this line we have 'mon = ...' which is a string
        lines[i-1] = "            mon_str = str(item.get('monthlyRent', '')).strip().replace(',', '')\n            mon = int(mon_str) if mon_str else 0\n"

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(''.join(lines))
