import os
import subprocess
import shutil

# In consult_diary/rosary.html:
with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Force cut the entire block from '<span id="introLangLabel"'
# Find the opening <div class="intro-section-card"> right before it
idx = text.find('id="introLangLabel"')
if idx != -1:
    card_start = text.rfind('<div class="intro-section-card">', 0, idx)
    # Find the closing </div> of this card (it contains intro-toggle-group)
    toggle_idx = text.find('class="intro-toggle-group"', idx)
    card_end = text.find('</div>', text.find('</div>', toggle_idx) + 1) + 6
    print("Found exact slice:", card_start, card_end)
    text = text[:card_start] + text[card_end:]
    print("SLICED OUT SUCCESSFULLY!")
else:
    print("introLangLabel NOT FOUND!")

# Also ensure btnHeaderLangToggle is in intro-top-actions
if 'id="btnHeaderLangToggle"' not in text:
    header_actions_target = '<div class="intro-top-actions">'
    lang_pill_button = """<div class="intro-top-actions">
          <button id="btnHeaderLangToggle" type="button" class="action-pill-btn" onclick="if(window.rosaryApp){var nextLang = window.rosaryApp.settings.lang === 'en' ? 'ko' : 'en'; window.rosaryApp.setLanguage(nextLang); var b=document.getElementById('btnHeaderLangToggle'); if(b) b.textContent = nextLang === 'en' ? '🌐 한' : '🌐 EN';}" style="height: 32px; padding: 0 10px; font-size: 0.78rem; font-weight: 700; margin-right: 4px; background: rgba(243, 198, 105, 0.12); border: 1px solid rgba(243, 198, 105, 0.35); color: var(--gold-primary); border-radius: 16px;">
            🌐 EN
          </button>"""
    text = text.replace(header_actions_target, lang_pill_button, 1)

# Check if 'introLangLabel' still exists in text
print("Still exists after slice?", "introLangLabel" in text)

with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text)

os.chdir("d:/부동산업무/antigravity/consult_diary")
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: surgically slice out introLangLabel card v110"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("SURGICAL_SLICE_DEPLOYED_SUCCESSFULLY")
