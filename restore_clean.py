import subprocess
import os

# 1. Restore sw.js to normal without deleting caches blindly
sw_code = """const CACHE_NAME = 'rosary-app-v61';

self.addEventListener('install', event => {
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  // Network first
});
"""

with open("d:/부동산업무/antigravity/consult_diary/sw.js", "w", encoding="utf-8") as f:
    f.write(sw_code)

# 2. Check rosary.html sw script - make sure it doesn't break
with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "r", encoding="utf-8") as f:
    html = f.read()

# Make sure manifest is manifest.json
html = html.replace('href="https://no1korealtor.github.io/consult_diary/rosary-manifest.json?v=51"', 'href="manifest.json?v=61"')
html = html.replace('href="rosary-manifest.json?v=50"', 'href="manifest.json?v=61"')

with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "w", encoding="utf-8") as f:
    f.write(html)

# 3. git push
os.chdir("d:/부동산업무/antigravity/consult_diary")
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: restore clean sw and manifest"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)
print("FIX_RESTORE_DONE")
