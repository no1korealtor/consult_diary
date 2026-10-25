import os
import subprocess
import shutil

# Completely clean bundle from rosary-app source files
ROSARY_DIR = "d:/부동산업무/antigravity/rosary-app"
CONSULT_DIR = "d:/부동산업무/antigravity/consult_diary"

os.chdir(ROSARY_DIR)

# 1. Read individual clean source files
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

with open("style.css", "r", encoding="utf-8") as f:
    css = f.read()

with open("rosary-data.js", "r", encoding="utf-8") as f:
    data_js = f.read()

yeondo_js = ""
if os.path.exists("yeondo-data.js"):
    with open("yeondo-data.js", "r", encoding="utf-8") as f:
        yeondo_js = f.read()

with open("app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

# 2. Strip any old embedded styles or redundant scripts in index.html
# Replace <link rel="stylesheet" href="style.css"> with <style>...</style>
html = html.replace('<link rel="stylesheet" href="style.css">', f'<style>\n{css}\n</style>')

# Replace scripts
bundle_scripts = f"""<script>
{data_js}

{yeondo_js}

{app_js}
</script>"""

# Find script tags at bottom
import re
html = re.sub(r'<script src="rosary-data.js"></script>.*?<script src="app.js"></script>', bundle_scripts, html, flags=re.DOTALL)

# Ensure cache busting query param on HTML title or meta
html = html.replace('<title>묵주기도 - 거룩한 묵상</title>', '<title>묵주기도 - 거룩한 묵상 v90</title>')

with open("rosary.html", "w", encoding="utf-8") as f:
    f.write(html)

# Copy to consult_diary
shutil.copy("rosary.html", os.path.join(CONSULT_DIR, "rosary.html"))

# Git push
os.chdir(CONSULT_DIR)
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "build: clean single-source bundle rosary.html v90"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("\n" + "="*50)
print("CLEAN_BUNDLE_V90_DEPLOYED_SUCCESSFULLY")
print("="*50)
