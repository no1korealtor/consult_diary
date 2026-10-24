import sys
import os

filepath = "building_viewer.py"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

idx = -1
for i, line in enumerate(lines):
    if line.rstrip() == "            if kakao_img or naver_img:":
        idx = i
        break

if idx != -1:
    for i in range(idx, len(lines)):
        if lines[i].startswith("            "): # 12 spaces
            lines[i] = lines[i][4:]
        elif lines[i].strip() == "":
            pass
        elif lines[i].startswith("        grnd_cnt_int = 0"):
            break
            
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("Patched building_viewer.py again")
else:
    print("block not found")
