import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect RosaryApp startPrayer
idx_goToStep = text.find("goToStep(index,")
if idx_goToStep != -1:
    print(text[idx_goToStep-10:idx_goToStep+300])
