with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if i >= 1581 and i <= 1645:
        # Dedent by 12 spaces (from 20 down to 8 spaces)
        if line.startswith("                    "):
            new_lines.append(line[12:])
        else:
            new_lines.append(line)
    elif i >= 1646 and i <= 1652:
        # We should NOT dedent the except block unless it matches the try block.
        # But wait! Where is the try block?
        # The try block was at 1378!
        # The try block is indented 4 spaces.
        # But `except Exception as t:` is at 1646, indented 16 spaces.
        # This means the `except` block was also mangled!
        # It should be dedented to 4 spaces!
        if line.startswith("                except") or line.startswith("                except Exception"):
            new_lines.append(line[12:]) # from 16 to 4 spaces
        elif line.startswith("                    "):
            new_lines.append(line[12:]) # from 20 to 8 spaces
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
