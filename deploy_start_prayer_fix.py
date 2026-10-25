import os
import subprocess
import shutil

# Make sure btnStartPrayer has guaranteed direct onclick:
with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "r", encoding="utf-8") as f:
    text = f.read()

# Replace btnStartPrayer with guaranteed handler
old_start = '<button type="button" id="btnStartPrayer" class="intro-main-start-btn">'
new_start = '<button type="button" id="btnStartPrayer" class="intro-main-start-btn" onclick="if(window.rosaryApp){window.rosaryApp.handleStartPrayerRequest();}">'

if old_start in text:
    text = text.replace(old_start, new_start)

# Also let's check if there is an unhandled exception in handleStartPrayerRequest
idx = text.find('handleStartPrayerRequest()')
print("handleStartPrayerRequest found:", idx != -1)
if idx != -1:
    print(text[idx:idx+400])

with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text)

# Git commit & push
os.chdir("d:/부동산업무/antigravity/consult_diary")
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: wire guaranteed direct onclick to btnStartPrayer"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("START_PRAYER_WIRED_SUCCESSFULLY")
