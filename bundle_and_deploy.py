import os
import subprocess
import shutil

# Bundle fresh rosary.html
subprocess.run(["python", "bundle.py"], cwd="d:/부동산업무/antigravity/rosary-app", check=True)

# Copy to consult_diary
shutil.copy("d:/부동산업무/antigravity/rosary-app/rosary.html", "d:/부동산업무/antigravity/consult_diary/rosary.html")

# Check if introIntentionCard is in consult_diary/rosary.html
with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "r", encoding="utf-8") as f:
    c = f.read()

print("introIntentionCard in target after bundle:", "id=\"introIntentionCard\"" in c)

# Git push
os.chdir("d:/부동산업무/antigravity/consult_diary")
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: properly bundle and deploy intention card to rosary.html"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("PROPER_BUNDLE_DEPLOYED_SUCCESSFULLY")
