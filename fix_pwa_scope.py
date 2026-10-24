import os
import subprocess
import sys

# 1. Update consult_diary/rosary-manifest.json with absolute path or full URL
manifest_content = """{
  "name": "묵주기도",
  "short_name": "묵주기도",
  "description": "가톨릭 성모 묵주기도 및 하느님 자비의 기도",
  "id": "/consult_diary/rosary.html",
  "start_url": "https://no1korealtor.github.io/consult_diary/rosary.html",
  "scope": "https://no1korealtor.github.io/consult_diary/",
  "display": "standalone",
  "background_color": "#0F172A",
  "theme_color": "#0F172A",
  "icons": [
    {
      "src": "https://no1korealtor.github.io/consult_diary/icons/rosary-gold-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "https://no1korealtor.github.io/consult_diary/icons/rosary-gold-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
"""

with open("d:/부동산업무/antigravity/consult_diary/rosary-manifest.json", "w", encoding="utf-8") as f:
    f.write(manifest_content)

# 2. Update consult_diary/sw.js to make it a valid PWA for rosary
sw_content = """const CACHE_NAME = 'rosary-pwa-v51';

self.addEventListener('install', event => {
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(clients.claim());
});

self.addEventListener('fetch', event => {
  // Let network handle directly
});
"""

with open("d:/부동산업무/antigravity/consult_diary/rosary-sw.js", "w", encoding="utf-8") as f:
    f.write(sw_content)

# 3. Add service worker registration and correct manifest in rosary.html
with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "r", encoding="utf-8") as f:
    html = f.read()

# Make sure manifest link is absolute
old_manifest = '<link rel="manifest" href="rosary-manifest.json?v=50">'
new_manifest = '<link rel="manifest" href="https://no1korealtor.github.io/consult_diary/rosary-manifest.json?v=51">'
if old_manifest in html:
    html = html.replace(old_manifest, new_manifest)

# Add SW registration if not present
if 'rosary-sw.js' not in html:
    sw_script = """<script>
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('./rosary-sw.js?v=51');
}
</script>
</body>"""
    html = html.replace('</body>', sw_script)

with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "w", encoding="utf-8") as f:
    f.write(html)

print("ALL_PWA_FILES_PREPARED")
