import os
import subprocess
import shutil

# 1. Inspect consult_diary/rosary.html
with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "r", encoding="utf-8") as f:
    text = f.read()

# Make introIntentionCard visible by default (display: block)
text = text.replace('id="introIntentionCard" class="intro-section-card intention-card" style="display: none;', 'id="introIntentionCard" class="intro-section-card intention-card" style="display: block;')

# Make sure it's also updated in rosary-app/index.html
with open("d:/부동산업무/antigravity/rosary-app/index.html", "r", encoding="utf-8") as f:
    idx_text = f.read()

idx_text = idx_text.replace('id="introIntentionCard" class="intro-section-card intention-card" style="display: none;', 'id="introIntentionCard" class="intro-section-card intention-card" style="display: block;')

with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(idx_text)

os.chdir("d:/부동산업무/antigravity/consult_diary")
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: make intention card display block by default with sample"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("CARD_VISIBLE_DEPLOYED")
