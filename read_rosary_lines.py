import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect around line 8700 to 8900
lines = text.splitlines()
print("\n".join(lines[8700:8800]))
