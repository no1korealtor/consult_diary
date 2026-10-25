import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect RosaryApp startPrayer
idx_sp = text.find("startPrayer(skipKissOverlay")
idx_proceed = text.find("const proceed = () =>", idx_sp)
print(text[idx_proceed:idx_proceed+400])
