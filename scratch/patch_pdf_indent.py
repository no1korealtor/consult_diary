with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.strip() == "for path in font_paths:":
        # Insert a try block around the inside of the loop
        pass

# I'll just use simple regex or replace for lines 969 to 976
new_lines = []
i = 0
while i < len(lines):
    if lines[i].startswith("        for path in font_paths:"):
        new_lines.append(lines[i])
        new_lines.append("            try:\n")
        new_lines.append("                if not os.path.exists(path):\n")
        new_lines.append("                    continue\n")
        new_lines.append("                pdfmetrics.registerFont(TTFont(\"KoreanFont\", path))\n")
        new_lines.append("                registered = True\n")
        new_lines.append("                break\n")
        new_lines.append("            except:\n")
        new_lines.append("                pass\n")
        i += 8 # Skip lines 970 to 977
    else:
        new_lines.append(lines[i])
        i += 1

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
