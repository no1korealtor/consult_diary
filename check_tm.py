import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect trackerModal in HTML
idx_tm = text.find('id="trackerModal"')
print("trackerModal found at:", idx_tm)
if idx_tm != -1:
    print(text[idx_tm-50:idx_tm+100])
