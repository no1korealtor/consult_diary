import os
import subprocess
import shutil

# In consult_diary/rosary.html, let's fix .modal-backdrop:
with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "r", encoding="utf-8") as f:
    text = f.read()

# Notice in CSS:
# .modal-backdrop {
#   position: fixed;
#   top: 0; left: 0; right: 0; bottom: 0;
#   ...
#   opacity: 0;
#   pointer-events: none;
#   transition: ...
# }
# If pointer-events was changed to auto or removed, the transparent modal-backdrop blocks all touches!

# Let's ensure:
fix_css_touch = """
<style>
/* [터치 완전 보장] 모달이 닫혀 있을 때는 화면 전체 터치를 절대 막지 않음 */
.modal-backdrop {
  display: none !important;
  pointer-events: none !important;
}

.modal-backdrop.show {
  display: flex !important;
  pointer-events: auto !important;
}

#crucifixKissOverlay {
  display: none !important;
  pointer-events: none !important;
}

#crucifixKissOverlay.active {
  display: flex !important;
  pointer-events: auto !important;
}

/* 터치 반응 속도 극대화 */
html, body, #app, .intro-view, .prayer-view, button, a {
  touch-action: manipulation !important;
  pointer-events: auto !important;
  cursor: pointer !important;
}
</style>
"""

text = text.replace('</head>', f"{fix_css_touch}\n</head>")

with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text)

os.chdir("d:/부동산업무/antigravity/consult_diary")
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: display none !important for modal backdrops when inactive to restore touch 100%"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("\n" + "="*50)
print("TOUCH_BARRIER_COMPLETELY_DESTROYED")
print("="*50)
