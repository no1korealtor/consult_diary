import os

with open("d:/부동산업무/antigravity/rosary-app/app.js", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("goToStep")
while idx != -1:
    line = text[max(0, text.rfind("\n", 0, idx)):text.find("\n", idx)]
    print(line)
    idx = text.find("goToStep", idx + 8)
