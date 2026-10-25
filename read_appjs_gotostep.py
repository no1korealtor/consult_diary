import os

with open("d:/부동산업무/antigravity/rosary-app/app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(1250, 1350):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end="")
