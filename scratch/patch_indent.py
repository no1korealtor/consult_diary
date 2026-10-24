import sys
import os

filepath = "building_viewer.py"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

out_lines = []
in_while = False
for i, line in enumerate(lines):
    if line.strip() == "while 1:" and "kakao_img or naver_img" in lines[i+1]:
        in_while = True
        continue
    
    if in_while:
        if line.startswith("                ") and not line.startswith("                    "):
            # This is 16 spaces (4 levels). If it drops below 16 spaces, while ends.
            # But wait, doc.build is indented 16 spaces!
            pass

# Actually let's just do a manual replace
# Find line 744 which is '            while 1:'
idx = -1
for i, line in enumerate(lines):
    if line.rstrip() == "            while 1:" and "kakao_img or naver_img" in lines[i+1]:
        idx = i
        break

if idx != -1:
    lines.pop(idx)
    # Dedent the next lines until we hit a line that is less indented than 16 spaces?
    # No, wait, doc.build was originally inside a try...except in the decompiled code?
    # Let's check lines from idx to idx+60
    for i in range(idx, len(lines)):
        if lines[i].startswith("                "):
            lines[i] = lines[i][4:]
        elif lines[i].strip() == "":
            pass
        elif lines[i].startswith("        grnd_cnt_int = 0"):
            break
            
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("Patched building_viewer.py")
else:
    print("while 1: not found")
