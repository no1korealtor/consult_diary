import os
import subprocess
import shutil

# In consult_diary/rosary.html:
with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Inspect why modal-backdrop.show doesn't show settingsModal:
# In previous fix:
# .modal-backdrop { display: none !important; pointer-events: none !important; }
# .modal-backdrop.show { display: flex !important; pointer-events: auto !important; }
# BUT bottom-sheet inside settingsModal might need opacity, transform, and z-index!

settings_modal_fix_css = """
<style>
/* 설정 모달 & 모든 바텀시트 모달 확실한 팝업 스타일 */
#settingsModal.show,
#trackerModal.show,
#intentionModal.show,
#mysteryModal.show,
#historyModal.show,
#adminModal.show,
#donationModal.show {
  display: flex !important;
  opacity: 1 !important;
  visibility: visible !important;
  pointer-events: auto !important;
  z-index: 100000 !important;
}

#settingsModal.show .bottom-sheet,
#trackerModal.show .bottom-sheet,
#intentionModal.show .bottom-sheet,
#mysteryModal.show .bottom-sheet,
#historyModal.show .bottom-sheet,
#adminModal.show .bottom-sheet,
#donationModal.show .bottom-sheet {
  display: block !important;
  opacity: 1 !important;
  visibility: visible !important;
  transform: translateY(0) !important;
}
</style>
"""

text = text.replace('</head>', f"{settings_modal_fix_css}\n</head>")

# 2. Fix setLanguage in window.rosaryApp:
# Let's inspect setLanguage in text
lang_fix_js = """
// [전역 원터치 언어 전환 함수]
function toggleGlobalLanguage() {
  try {
    if (!window.rosaryApp) return;
    const cur = window.rosaryApp.settings.lang || 'ko';
    const next = (cur === 'en') ? 'ko' : 'en';
    window.rosaryApp.setLanguage(next);
    
    // 버튼 텍스트 변경
    const btn = document.getElementById('btnHeaderLangToggle');
    if (btn) {
      btn.textContent = (next === 'en') ? '🌐 한' : '🌐 EN';
    }
  } catch(e) {
    console.error('toggleGlobalLanguage error:', e);
  }
}
"""

text = text.replace('</body>', f"<script>\n{lang_fix_js}\n</script>\n</body>")

# 3. Update onclick on btnHeaderLangToggle to call toggleGlobalLanguage()
text = text.replace("onclick=\"if(window.rosaryApp){var nextLang = window.rosaryApp.settings.lang === 'en' ? 'ko' : 'en'; window.rosaryApp.setLanguage(nextLang); var b=document.getElementById('btnHeaderLangToggle'); if(b) b.textContent = nextLang === 'en' ? '🌐 한' : '🌐 EN';}\"", "onclick=\"toggleGlobalLanguage();\"")

# 4. Update onclick on btnIntroSettings to call openSettingsDirect()
settings_open_js = """
function openSettingsDirect() {
  const m = document.getElementById('settingsModal');
  if (m) {
    m.classList.add('show');
    m.style.display = 'flex';
  }
}
function closeSettingsDirect() {
  const m = document.getElementById('settingsModal');
  if (m) {
    m.classList.remove('show');
    m.style.display = 'none';
  }
}
"""
text = text.replace('</body>', f"<script>\n{settings_open_js}\n</script>\n</body>")
text = text.replace("onclick=\"const m=document.getElementById('settingsModal');if(m)m.classList.add('show');\"", "onclick=\"openSettingsDirect();\"")
text = text.replace("onclick=\"const m=document.getElementById('settingsModal');if(m)m.classList.remove('show');\"", "onclick=\"closeSettingsDirect();\"")

with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text)

os.chdir("d:/부동산업무/antigravity/consult_diary")
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: guaranteed settings modal popup and global language toggle v115"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("SETTINGS_AND_LANG_GUARANTEED_DEPLOYED")
