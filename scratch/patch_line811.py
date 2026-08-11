with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.strip() == 'def get_numeric_averages(subset, is_rent, is_wolse):':
        lines[i] = '        def get_numeric_averages(subset, is_rent, is_wolse=False):\n'

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
