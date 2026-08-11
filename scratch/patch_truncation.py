import os

with open('restructure.py', 'r', encoding='utf-8') as f:
    r_lines = f.readlines()

missing_part = []
started = False
for line in r_lines:
    if 'console_content = "\\n".join(report_lines)' in line:
        started = True
    if started:
        if line.strip() == '"""':
            break
        missing_part.append(line)

with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    t_lines = f.readlines()

# Find where it was truncated
idx = -1
for i, line in enumerate(t_lines):
    if 'console_content = "\\n".join(report_lines)' in line:
        idx = i
        break

if idx != -1:
    new_t_lines = t_lines[:idx] + missing_part
    with open('trade_viewer.py', 'w', encoding='utf-8') as f:
        f.writelines(new_t_lines)
