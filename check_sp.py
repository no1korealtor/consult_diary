import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect RosaryApp startPrayer
idx_sp = text.find("startPrayer(skipKissOverlay")
if idx_sp == -1:
    idx_sp = text.find("startPrayer(")
print("startPrayer pos:", idx_sp)
if idx_sp != -1:
    print(text[idx_sp-30:idx_sp+500])
