import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

has_goToStep_def = "goToStep(index, isManual = false)" in text or "goToStep(stepIndex" in text
print("Has goToStep definition in text?", has_goToStep_def)

# Find if goToStep definition was omitted or named differently!
lines = text.splitlines()
for i, line in enumerate(lines):
    if "goToStep(" in line and "this.goToStep" not in line and "rosaryApp.goToStep" not in line:
        print(f"Line {i+1}: {line}")
