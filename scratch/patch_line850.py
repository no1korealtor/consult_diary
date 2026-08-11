with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.strip() == 'def get_avg_display(subset, is_rent, is_wolse=False):':
        lines[i] = '        def get_avg_display(subset, is_rent, is_wolse=False):\n            avg_data = get_numeric_averages(subset, is_rent, is_wolse)\n'

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
