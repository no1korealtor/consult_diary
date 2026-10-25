import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

print("goToStep in rosary.html line numbers:")
lines = text.splitlines()
for i, line in enumerate(lines):
    if "goToStep(index," in line or "goToStep(index)" in line or "goToStep = function" in line:
        print(f"rosary.html line {i+1}: {line}")
