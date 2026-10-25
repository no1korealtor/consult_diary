import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    lines_rosary = f.readlines()

with open("d:/부동산업무/antigravity/rosary-app/app.js", "r", encoding="utf-8") as f:
    text_appjs = f.read()

# In app.js find goToStep
idx1 = text_appjs.find("goToStep(index, isManual = false) {")
idx2 = text_appjs.find("renderCurrentStep(isManual = false) {", idx1)

missing_gotostep_code = text_appjs[idx1:idx2]
print("Found missing goToStep code from app.js! Length:", len(missing_gotostep_code))

# Insert this method before renderCurrentStep in rosary.html
text_rosary = "".join(lines_rosary)
target_insert = "renderCurrentStep(isManual = false) {"
if target_insert in text_rosary:
    text_rosary = text_rosary.replace(target_insert, missing_gotostep_code + "\n  " + target_insert)
    print("Successfully restored goToStep method into RosaryApp in rosary.html!")

with open(path, "w", encoding="utf-8") as f:
    f.write(text_rosary)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text_rosary)

print("Saved files successfully!")
