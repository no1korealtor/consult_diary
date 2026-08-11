with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if line.strip() == "None" and "table_cell_style_right" in lines[i+1]:
        new_lines.append("                break\n")
        new_lines.append("            except:\n")
        new_lines.append("                pass\n")
    elif line.strip() == "table_cell_style_right":
        continue
    elif i >= 1361 and i <= 1374:
        # lines 1362 to 1375 (0-indexed 1361 to 1374)
        continue
    else:
        new_lines.append(line)

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
