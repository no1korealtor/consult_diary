with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_func = False
for i in range(len(lines)):
    if "def save_briefing_report(" in lines[i]:
        in_func = True
        
    if in_func and "if not trades and not jeonses and not wolses:" in lines[i]:
        lines[i] = '    print("Checking if empty")\n' + lines[i]
        
    if in_func and "def save_briefing_report_pdf" in lines[i]:
        break
        
    if in_func and 'save_dir = "시세브리핑"' in lines[i]:
        lines[i] = '    print("Creating save_dir")\n' + lines[i]
        
    if in_func and "report_lines = []" in lines[i]:
        lines[i] = '    print("Appending to report_lines")\n' + lines[i]
        
    if in_func and 'filename = os.path.join' in lines[i]:
        lines[i] = '    print("Defining filename")\n' + lines[i]
        
    if in_func and 'with open(filename, "w"' in lines[i]:
        lines[i] = '    print("Opening file to write")\n' + lines[i]

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(''.join(lines))
