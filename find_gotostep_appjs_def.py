import os

with open("d:/부동산업무/antigravity/rosary-app/app.js", "r", encoding="utf-8") as f:
    text = f.read()

lines = text.splitlines()
for i, line in enumerate(lines):
    if "goToStep(" in line and "this.goToStep" not in line:
        print(f"app.js Line {i+1}: {line}")
