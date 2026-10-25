import os
import sys

# Bundle rosary.html directly from index.html, style.css, rosary-data.js, yeondo-data.js, app.js
ROSARY_DIR = "d:/부동산업무/antigravity/rosary-app"
CONSULT_DIR = "d:/부동산업무/antigravity/consult_diary"

os.chdir(ROSARY_DIR)

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('style.css', 'r', encoding='utf-8') as f:
    css = f.read()

with open('rosary-data.js', 'r', encoding='utf-8') as f:
    data_js = f.read()

yeondo_js = ""
if os.path.exists('yeondo-data.js'):
    with open('yeondo-data.js', 'r', encoding='utf-8') as f:
        yeondo_js = f.read()

with open('app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# Replace css link
html = html.replace('<link rel="stylesheet" href="style.css">', f'<style>\n{css}\n</style>')

# Replace script tags
target = '<script src="rosary-data.js"></script>\n  <script src="yeondo-data.js"></script>\n  <script src="app.js"></script>'
replacement = f'<script>\n{data_js}\n\n{yeondo_js}\n\n{app_js}\n</script>'
if target in html:
    html = html.replace(target, replacement)
else:
    t2 = '<script src="rosary-data.js"></script>\n  <script src="app.js"></script>'
    html = html.replace(t2, replacement)

with open('rosary.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Copy to consult_diary
import shutil
shutil.copy('rosary.html', os.path.join(CONSULT_DIR, 'rosary.html'))

# Git push
os.chdir(CONSULT_DIR)
import subprocess
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "feat: 4 mysteries sacred art dynamic artwork for crucifix kiss v80"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("\n" + "="*50)
print("SUCCESS! 4 MYSTERIES SACRED ART DEPLOYED TO GITHUB!")
print("="*50)
