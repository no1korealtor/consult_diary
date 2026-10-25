import os
import subprocess
import shutil

ROSARY_DIR = "d:/부동산업무/antigravity/rosary-app"
CONSULT_DIR = "d:/부동산업무/antigravity/consult_diary"

with open(os.path.join(ROSARY_DIR, "index.html"), "r", encoding="utf-8") as f:
    html = f.read()

# 1. Fix Settings Modal & Button:
# Ensure btnIntroSettings has direct inline click to open settingsModal!
old_setting_btn = '<button id="btnIntroSettings" class="icon-btn" aria-label="설정" title="설정">'
new_setting_btn = '<button id="btnIntroSettings" class="icon-btn" onclick="const m=document.getElementById(\'settingsModal\');if(m)m.classList.add(\'show\');" aria-label="설정" title="설정">'
if old_setting_btn in html:
    html = html.replace(old_setting_btn, new_setting_btn)

# 2. Fix Crucifix Kiss Overlay: Ensure it is fixed, full screen, z-index 99999, and immediately shows!
kiss_css_perfect = """
<style>
/* 십자가 친구(親吻) 성화 전체화면 완벽 강제 노출 */
#crucifixKissOverlay {
  display: none !important;
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  height: 100dvh !important;
  background: radial-gradient(circle at center, #1b2845 0%, #080c14 100%) !important;
  z-index: 999999 !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  opacity: 0 !important;
  pointer-events: none !important;
  transition: opacity 0.35s ease !important;
}

#crucifixKissOverlay.active {
  display: flex !important;
  opacity: 1 !important;
  pointer-events: auto !important;
}

#crucifixKissOverlay.active .kiss-crucifix-target {
  animation: holyPulse 2s infinite ease-in-out !important;
}

@keyframes holyPulse {
  0% { transform: scale(1); filter: drop-shadow(0 0 15px rgba(243, 198, 105, 0.5)); }
  50% { transform: scale(1.04); filter: drop-shadow(0 0 28px rgba(243, 198, 105, 0.85)); }
  100% { transform: scale(1); filter: drop-shadow(0 0 15px rgba(243, 198, 105, 0.5)); }
}
</style>
"""

html = html.replace("</head>", f"{kiss_css_perfect}\n</head>")

with open(os.path.join(ROSARY_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

# Bundle
subprocess.run(["python", "bundle.py"], cwd=ROSARY_DIR, check=True)

# Copy to consult_diary
shutil.copy(os.path.join(ROSARY_DIR, "rosary.html"), os.path.join(CONSULT_DIR, "rosary.html"))

# Git push
os.chdir(CONSULT_DIR)
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: crucifix kiss overlay visibility z-index and settings modal click"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("CRUCIFIX_KISS_AND_SETTINGS_DEPLOYED_SUCCESSFULLY")
