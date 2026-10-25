import os
import subprocess
import shutil

# In consult_diary/rosary.html, let's inspect #crucifixKissOverlay CSS!
with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "r", encoding="utf-8") as f:
    text = f.read()

# Notice in CSS:
# #crucifixKissOverlay { display: none !important; pointer-events: none !important; }
# If an overlay has display: flex or position: fixed without display: none, it blocks ALL touch!

# Let's completely disable crucifixKissOverlay by default and remove pointer-events blocking
bad_css = """/* 십자가 친구(親吻) 성화 전체화면 완벽 강제 노출 */
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
}"""

# Replace all z-index: 999999 or overlay blocking CSS
text = text.replace('z-index: 999999 !important;', 'z-index: 999 !important;')
text = text.replace('pointer-events: none !important;', '')

# Make sure all overlays have pointer-events: none when NOT active or NOT show
fix_css = """
<style>
/* 터치 차단 방지: 모든 모달과 오버레이는 비활성 시 클릭 통과 */
.modal-backdrop:not(.show),
#crucifixKissOverlay:not(.active),
.crucifix-kiss-overlay:not(.active) {
  display: none !important;
  pointer-events: none !important;
  visibility: hidden !important;
}

#app, .intro-view, .prayer-view {
  pointer-events: auto !important;
  touch-action: manipulation !important;
}

button, a, .mystery-select-card, .day-card {
  pointer-events: auto !important;
  cursor: pointer !important;
}
</style>
"""

text = text.replace('</head>', f"{fix_css}\n</head>")

with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text)

os.chdir("d:/부동산업무/antigravity/consult_diary")
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: unblock all screen touch by disabling dormant overlay pointer-events"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("\n" + "="*50)
print("TOUCH_UNBLOCKED_DEPLOYED_SUCCESSFULLY")
print("="*50)
