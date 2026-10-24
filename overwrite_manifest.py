import shutil
import subprocess

# 1. Overwrite icon.png in consult_diary root with rosary gold 192 icon!
shutil.copy("d:/부동산업무/antigravity/consult_diary/icons/rosary-gold-192.png", "d:/부동산업무/antigravity/consult_diary/icon.png")

# 2. Overwrite consult_diary/sw.js cache
sw_code = """const CACHE_NAME = 'rosary-direct-v60';

self.addEventListener('install', event => {
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.map(k => caches.delete(k))))
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  // bypass cache
});
"""
with open("d:/부동산업무/antigravity/consult_diary/sw.js", "w", encoding="utf-8") as f:
    f.write(sw_code)

# 3. git push
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: overwrite root manifest and icon with rosary gold"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)
print("SUCCESS_OVERWRITE")
