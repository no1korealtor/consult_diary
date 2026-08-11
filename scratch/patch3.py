with open('restructure.py', 'r', encoding='utf-8') as f:
    text = f.read()

parts = text.split('console_content = "\\\\n".join(report_lines)\n')
missing = parts[1].split('"""')[0]

with open('trade_viewer.py', 'a', encoding='utf-8') as f:
    f.write('        console_content = "\\n".join(report_lines)\n' + missing)
