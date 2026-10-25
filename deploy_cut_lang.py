import os
import subprocess
import shutil

# In consult_diary/rosary.html:
with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Remove the entire "기도 언어 (Language)" section card:
# Find <span id="introLangLabel" class="intro-card-title">기도 언어 (Language)</span>
# and find the surrounding <div class="intro-section-card"> ... </div>
import re

lang_card_pattern = r'<div class="intro-section-card">\s*<div class="intro-card-header">\s*<span class="intro-card-icon">🌐</span>\s*<span id="introLangLabel"[^>]*>.*?</div>\s*<div class="intro-toggle-group">.*?</div>\s*</div>'
match = re.search(lang_card_pattern, text, re.DOTALL)
if match:
    text = text[:match.start()] + text[match.end():]
    print("Found and eradicated big language card completely!")
else:
    print("Direct pattern not matched, attempting split removal")
    idx = text.find('id="introLangLabel"')
    if idx != -1:
        card_start = text.rfind('<div class="intro-section-card">', 0, idx)
        card_end = text.find('</div>\n        </div>', idx) + 15
        text = text[:card_start] + text[card_end:]
        print("Removed via fallback index slice!")

# 2. Add [ 🌐 EN ] pill to top header actions
if 'id="btnHeaderLangToggle"' not in text:
    header_actions_target = '<div class="intro-top-actions">'
    lang_pill_button = """<div class="intro-top-actions">
          <button id="btnHeaderLangToggle" type="button" class="action-pill-btn" onclick="if(window.rosaryApp){var nextLang = window.rosaryApp.settings.lang === 'en' ? 'ko' : 'en'; window.rosaryApp.setLanguage(nextLang); var b=document.getElementById('btnHeaderLangToggle'); if(b) b.textContent = nextLang === 'en' ? '🌐 한' : '🌐 EN';}" style="height: 32px; padding: 0 10px; font-size: 0.78rem; font-weight: 700; margin-right: 4px; background: rgba(243, 198, 105, 0.12); border: 1px solid rgba(243, 198, 105, 0.35); color: var(--gold-primary); border-radius: 16px;">
            🌐 EN
          </button>"""
    text = text.replace(header_actions_target, lang_pill_button, 1)

with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text)

os.chdir("d:/부동산업무/antigravity/consult_diary")
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: permanently cut large language card from rosary.html and index.html v105"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("\n" + "="*50)
print("LARGE_LANG_CARD_PERMANENTLY_REMOVED")
print("="*50)
