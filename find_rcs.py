import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect where renderCurrentStep is defined
idx = text.find("renderCurrentStep(")
print("renderCurrentStep position:", idx)
if idx != -1:
    print(text[idx-50:idx+400])
