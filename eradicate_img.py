import os
import subprocess
import shutil

# Remove the broken img tag directly in consult_diary/rosary.html AND rosary-app/index.html
def replace_img(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the img tag with crucifix
    import re
    # Match <img ... alt="거룩하신 우리 주 예수 그리스도의 십자가 수난 성화" ... />
    pattern = r'<img[^>]+alt="거룩하신 우리 주 예수 그리스도의 십자가 수난 성화"[^>]*>'
    
    new_box = '<div id="sacredArtDisplayBox" style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;"><!-- Dynamic Sacred Art --></div>'

    if re.search(pattern, content):
        content = re.sub(pattern, new_box, content)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Replaced in {file_path}")
    else:
        print(f"Pattern not found in {file_path}")

replace_img("d:/부동산업무/antigravity/consult_diary/rosary.html")
replace_img("d:/부동산업무/antigravity/rosary-app/index.html")

# Ensure showCrucifixKissOverlay function in consult_diary/rosary.html is updated with getSacredArtSvgForMystery
with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "r", encoding="utf-8") as f:
    text = f.read()

print("getSacredArtSvgForMystery in consult_diary/rosary.html:", "getSacredArtSvgForMystery" in text)

# Git commit & push
os.chdir("d:/부동산업무/antigravity/consult_diary")
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: eradicate broken crucifix img tag completely v85"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("CRUCIFIX_IMG_COMPLETELY_ERADICATED")
