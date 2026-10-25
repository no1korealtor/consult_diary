import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect lines 8620 to 8655
lines = text.splitlines()
print("\n".join(lines[8620:8655]))
