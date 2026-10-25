import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect RosaryApp.goToStep implementation
idx = text.find("goToStep(stepIndex")
if idx == -1:
    idx = text.find("goToStep(")
print("goToStep found at:", idx)
if idx != -1:
    print(text[idx-20:idx+400])
