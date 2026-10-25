import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect where RosaryApp goToStep is defined
idx = text.find("goToStep(")
while idx != -1:
    print(text[idx-30:idx+80])
    idx = text.find("goToStep(", idx + 10)
