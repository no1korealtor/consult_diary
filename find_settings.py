import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Check where settingsModal is
idx = text.find('id="settingsModal"')
print("settingsModal position:", idx)
if idx != -1:
    print("Around settingsModal:\n", text[idx-50:idx+400])
