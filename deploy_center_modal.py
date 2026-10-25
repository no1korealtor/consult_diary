import os
import subprocess
import shutil

ROSARY_DIR = "d:/부동산업무/antigravity/rosary-app"
CONSULT_DIR = "d:/부동산업무/antigravity/consult_diary"

with open(os.path.join(ROSARY_DIR, "index.html"), "r", encoding="utf-8") as f:
    html = f.read()

# Add CSS to style #resumeConfirmModal as a beautiful centered pop-up modal!
modal_css = """
<style>
/* 이어하기 확인 모달: 화면 중앙에 또렷하고 단정하게 즉시 나타나도록 완벽 스타일링 */
#resumeConfirmModal.show {
  display: flex !important;
  opacity: 1 !important;
  pointer-events: auto !important;
  align-items: center !important;
  justify-content: center !important;
}

#resumeConfirmModal .bottom-sheet {
  position: relative !important;
  bottom: auto !important;
  left: auto !important;
  width: 90% !important;
  max-width: 380px !important;
  margin: auto !important;
  border-radius: 20px !important;
  transform: scale(1) translateY(0) !important;
  opacity: 1 !important;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(243, 198, 105, 0.3) !important;
  animation: popInModal 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
}

@keyframes popInModal {
  0% { transform: scale(0.92) translateY(20px); opacity: 0; }
  100% { transform: scale(1) translateY(0); opacity: 1; }
}

/* 십자가 친구 성화 오버레이가 정상적으로 나타나도록 스타일 보장 */
#crucifixKissOverlay.active {
  display: flex !important;
  opacity: 1 !important;
  pointer-events: auto !important;
}
</style>
"""

if "popInModal" not in html:
    html = html.replace("</head>", f"{modal_css}\n</head>")

with open(os.path.join(ROSARY_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

# Bundle
subprocess.run(["python", "bundle.py"], cwd=ROSARY_DIR, check=True)

# Copy to consult_diary
shutil.copy(os.path.join(ROSARY_DIR, "rosary.html"), os.path.join(CONSULT_DIR, "rosary.html"))

# Git push
os.chdir(CONSULT_DIR)
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: make resume confirm modal pop up at center without swiping up"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("CENTER_MODAL_DEPLOYED_SUCCESSFULLY")
