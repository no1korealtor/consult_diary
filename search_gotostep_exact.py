import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect where RosaryApp goToStep is in the class
idx = text.find("goToStep(index,")
if idx == -1:
    idx = text.find("goToStep(")
    print("Found goToStep at:", idx)
    # search backwards for method start
    print(text[idx-50:idx+300])
