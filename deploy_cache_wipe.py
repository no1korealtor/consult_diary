import os
import subprocess
import shutil

# Unregister ALL service workers in rosary.html so client ALWAYS gets 100% fresh files without cache lock!
with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "r", encoding="utf-8") as f:
    text = f.read()

# Replace any service worker registration with an unregister script that wipes all cache!
sw_wipe_script = """<script>
// [캐시 강제 초기화] 서비스워커를 완전히 해제하고 최신 서버 파일을 100% 즉시 반영
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(function(registrations) {
    for (let registration of registrations) {
      registration.unregister();
    }
  });
}
if ('caches' in window) {
  caches.keys().then(function(names) {
    for (let name of names) {
      caches.delete(name);
    }
  });
}
</script>"""

import re
text = re.sub(r'<script>\s*if\s*\(\'serviceWorker\' in navigator\)[^<]+</script>', '', text)
text = text.replace('</body>', f"{sw_wipe_script}\n</body>")

# Also ensure direct onclick handlers on:
# 1. btnIntroLangKo
# 2. btnIntroLangEn
# 3. btnIntroSettings
# 4. btnDismissSettingsModal

text = text.replace('id="btnIntroLangKo" class="intro-toggle-btn active"', 'id="btnIntroLangKo" class="intro-toggle-btn active" onclick="if(window.rosaryApp){window.rosaryApp.setLanguage(\'ko\');}"')
text = text.replace('id="btnIntroLangEn" class="intro-toggle-btn"', 'id="btnIntroLangEn" class="intro-toggle-btn" onclick="if(window.rosaryApp){window.rosaryApp.setLanguage(\'en\');}"')

# Settings button
text = text.replace('id="btnIntroSettings" class="icon-btn"', 'id="btnIntroSettings" class="icon-btn" onclick="const m=document.getElementById(\'settingsModal\');if(m)m.classList.add(\'show\');"')
text = text.replace('id="closeSettingsBtn"', 'id="closeSettingsBtn" onclick="const m=document.getElementById(\'settingsModal\');if(m)m.classList.remove(\'show\');"')
text = text.replace('id="btnDismissSettingsModal"', 'id="btnDismissSettingsModal" onclick="const m=document.getElementById(\'settingsModal\');if(m)m.classList.remove(\'show\');"')

with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text)

# Also update sw.js and rosary-sw.js to self-destruct
self_destruct_sw = """
self.addEventListener('install', e => self.skipWaiting());
self.addEventListener('activate', e => {
  self.registration.unregister();
  self.clients.claim();
});
"""
with open("d:/부동산업무/antigravity/consult_diary/sw.js", "w", encoding="utf-8") as f:
    f.write(self_destruct_sw)

if os.path.exists("d:/부동산업무/antigravity/consult_diary/rosary-sw.js"):
    with open("d:/부동산업무/antigravity/consult_diary/rosary-sw.js", "w", encoding="utf-8") as f:
        f.write(self_destruct_sw)

os.chdir("d:/부동산업무/antigravity/consult_diary")
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: wipe service worker cache lock and bind direct onclick for language & settings"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("CACHE_WIPE_AND_ONCLICK_DEPLOYED_SUCCESSFULLY")
