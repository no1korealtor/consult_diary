import os
import subprocess
import sys
import shutil

ROSARY_DIR = "d:/부동산업무/antigravity/rosary-app"
CONSULT_DIR = "d:/부동산업무/antigravity/consult_diary"

with open(os.path.join(ROSARY_DIR, "index.html"), "r", encoding="utf-8") as f:
    html = f.read()

# Make sure manifest link has rel="manifest" with explicit type and cross-origin
old_link = '<link rel="manifest" href="manifest.json?v=61">'
new_link = '<link rel="manifest" href="./manifest.json">'
if old_link in html:
    html = html.replace(old_link, new_link)

with open(os.path.join(ROSARY_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

# Bundle
subprocess.run([sys.executable, "bundle.py"], cwd=ROSARY_DIR, check=True)

# Copy
shutil.copy(os.path.join(ROSARY_DIR, "rosary.html"), os.path.join(CONSULT_DIR, "rosary.html"))

# Git push
os.chdir(CONSULT_DIR)
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: pwa manifest link relative clean"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("MANIFEST_FIX_DEPLOYED")
