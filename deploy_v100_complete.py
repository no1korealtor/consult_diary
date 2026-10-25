import os
import subprocess
import shutil

# In consult_diary/rosary.html and rosary-app/index.html:
# 1. Remove the huge "기도 언어 (Language)" card from the main body completely!
# 2. Add the compact "[ 🌐 EN / 한 ]" button to the top header right next to the brand name or actions!
# 3. Wire the 4-mystery sacred art into showCrucifixKissOverlay directly in rosary.html so the artwork changes per mystery!

with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Remove big language card
old_lang_card_start = '<!-- 1. 언어 선택 카드 (한국어 / English) -->'
old_lang_card_end = '<!-- 2. 기도 종류 선택 카드'

if old_lang_card_start in text:
    idx1 = text.find(old_lang_card_start)
    idx2 = text.find(old_lang_card_end)
    text = text[:idx1] + text[idx2:]
    print("Removed big language card successfully!")

# 2. Add [ 🌐 EN ] pill button to top header
# In top header actions:
header_actions_target = '<div class="intro-top-actions">'
lang_pill_button = """<div class="intro-top-actions">
          <button id="btnHeaderLangToggle" type="button" class="action-pill-btn" onclick="if(window.rosaryApp){var nextLang = window.rosaryApp.settings.lang === 'en' ? 'ko' : 'en'; window.rosaryApp.setLanguage(nextLang); var b=document.getElementById('btnHeaderLangToggle'); if(b) b.textContent = nextLang === 'en' ? '🌐 한' : '🌐 EN';}" style="height: 32px; padding: 0 10px; font-size: 0.78rem; font-weight: 700; margin-right: 4px; background: rgba(243, 198, 105, 0.12); border: 1px solid rgba(243, 198, 105, 0.35); color: var(--gold-primary); border-radius: 16px;">
            🌐 EN
          </button>"""

if header_actions_target in text and "id=\"btnHeaderLangToggle\"" not in text:
    text = text.replace(header_actions_target, lang_pill_button, 1)
    print("Added top header lang toggle pill!")

# 3. Add 4-mystery sacred art dynamically in showCrucifixKissOverlay
# Let's inspect where showCrucifixKissOverlay is in text
art_generator_code = """
  // 4대 신비별 맞춤 성화 생성기
  getSacredArtForCurrentMystery() {
    const key = (this.currentPrayerType === 'divine_mercy') ? 'dm' : (this.currentMysteryKey || 'joyful');
    if (key === 'dm') {
      return `
        <svg viewBox="0 0 200 280" style="width:100%; height:100%; filter: drop-shadow(0 0 22px rgba(239, 68, 68, 0.7));">
          <defs>
            <radialGradient id="dmAura" cx="50%" cy="35%" r="60%">
              <stop offset="0%" stop-color="#FFFDF0"/>
              <stop offset="50%" stop-color="#FDE047" stop-opacity="0.4"/>
              <stop offset="100%" stop-color="#0F172A" stop-opacity="0"/>
            </radialGradient>
            <linearGradient id="redRay" x1="50%" y1="40%" x2="20%" y2="100%">
              <stop offset="0%" stop-color="#EF4444" stop-opacity="0.95"/>
              <stop offset="100%" stop-color="#B91C1C" stop-opacity="0"/>
            </linearGradient>
            <linearGradient id="paleRay" x1="50%" y1="40%" x2="80%" y2="100%">
              <stop offset="0%" stop-color="#E0F2FE" stop-opacity="0.95"/>
              <stop offset="100%" stop-color="#38BDF8" stop-opacity="0"/>
            </linearGradient>
          </defs>
          <circle cx="100" cy="90" r="80" fill="url(#dmAura)"/>
          <polygon points="100,105 20,280 80,280" fill="url(#redRay)"/>
          <polygon points="100,105 120,280 180,280" fill="url(#paleRay)"/>
          <circle cx="100" cy="55" r="22" fill="#FDE68A" stroke="#D97706" stroke-width="2"/>
          <path d="M85,75 Q100,70 115,75 L125,250 L75,250 Z" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5"/>
          <circle cx="100" cy="105" r="8" fill="#EF4444"/>
          <text x="100" y="272" text-anchor="middle" fill="#F3C669" font-size="11" font-weight="bold">예수님, 저는 당신께 의탁합니다</text>
        </svg>`;
    } else if (key === 'joyful') {
      return `
        <svg viewBox="0 0 200 280" style="width:100%; height:100%; filter: drop-shadow(0 0 24px rgba(72, 187, 120, 0.75));">
          <defs>
            <radialGradient id="joyHalo" cx="50%" cy="40%" r="65%">
              <stop offset="0%" stop-color="#FEF3C7"/>
              <stop offset="45%" stop-color="#6EE7B7" stop-opacity="0.45"/>
              <stop offset="100%" stop-color="#0F172A" stop-opacity="0"/>
            </radialGradient>
          </defs>
          <circle cx="100" cy="110" r="85" fill="url(#joyHalo)"/>
          <rect x="88" y="20" width="24" height="230" rx="8" fill="#F5C542" stroke="#B8860B" stroke-width="2.5"/>
          <rect x="35" y="65" width="130" height="24" rx="8" fill="#F5C542" stroke="#B8860B" stroke-width="2.5"/>
          <circle cx="100" cy="77" r="30" fill="#FFFDF0" stroke="#F5C542" stroke-width="2"/>
          <text x="100" y="86" text-anchor="middle" font-size="24">🌹</text>
          <text x="100" y="48" text-anchor="middle" font-size="18">🕊️</text>
          <rect x="55" y="225" width="90" height="24" rx="12" fill="rgba(15,23,42,0.9)" stroke="#6EE7B7" stroke-width="1.5"/>
          <text x="100" y="241" text-anchor="middle" fill="#A7F3D0" font-size="11" font-weight="bold">환희의 신비 성화</text>
        </svg>`;
    } else if (key === 'luminous') {
      return `
        <svg viewBox="0 0 200 280" style="width:100%; height:100%; filter: drop-shadow(0 0 26px rgba(66, 153, 225, 0.85));">
          <defs>
            <radialGradient id="lumHalo" cx="50%" cy="40%" r="70%">
              <stop offset="0%" stop-color="#FFFFFF"/>
              <stop offset="40%" stop-color="#60A5FA" stop-opacity="0.55"/>
              <stop offset="100%" stop-color="#0F172A" stop-opacity="0"/>
            </radialGradient>
          </defs>
          <circle cx="100" cy="110" r="90" fill="url(#lumHalo)"/>
          <rect x="88" y="20" width="24" height="230" rx="8" fill="#F5C542" stroke="#B8860B" stroke-width="2.5"/>
          <rect x="35" y="65" width="130" height="24" rx="8" fill="#F5C542" stroke="#B8860B" stroke-width="2.5"/>
          <circle cx="100" cy="77" r="30" fill="#EFF6FF" stroke="#3B82F6" stroke-width="2"/>
          <text x="100" y="86" text-anchor="middle" font-size="24">💡</text>
          <text x="100" y="48" text-anchor="middle" font-size="18">✨</text>
          <rect x="55" y="225" width="90" height="24" rx="12" fill="rgba(15,23,42,0.9)" stroke="#93C5FD" stroke-width="1.5"/>
          <text x="100" y="241" text-anchor="middle" fill="#BFDBFE" font-size="11" font-weight="bold">빛의 신비 성화</text>
        </svg>`;
    } else if (key === 'sorrowful') {
      return `
        <svg viewBox="0 0 200 280" style="width:100%; height:100%; filter: drop-shadow(0 0 26px rgba(229, 62, 62, 0.85));">
          <defs>
            <radialGradient id="sorHalo" cx="50%" cy="40%" r="65%">
              <stop offset="0%" stop-color="#FEE2E2"/>
              <stop offset="45%" stop-color="#EF4444" stop-opacity="0.45"/>
              <stop offset="100%" stop-color="#0F172A" stop-opacity="0"/>
            </radialGradient>
          </defs>
          <circle cx="100" cy="110" r="85" fill="url(#sorHalo)"/>
          <rect x="88" y="20" width="24" height="230" rx="8" fill="#D97706" stroke="#78350F" stroke-width="2.5"/>
          <rect x="35" y="65" width="130" height="24" rx="8" fill="#D97706" stroke="#78350F" stroke-width="2.5"/>
          <circle cx="100" cy="77" r="30" fill="#450A0A" stroke="#EF4444" stroke-width="2"/>
          <text x="100" y="86" text-anchor="middle" font-size="24">✝️</text>
          <text x="100" y="48" text-anchor="middle" font-size="18">🩸</text>
          <rect x="55" y="225" width="90" height="24" rx="12" fill="rgba(15,23,42,0.9)" stroke="#F87171" stroke-width="1.5"/>
          <text x="100" y="241" text-anchor="middle" fill="#FECACA" font-size="11" font-weight="bold">고통의 신비 성화</text>
        </svg>`;
    } else {
      return `
        <svg viewBox="0 0 200 280" style="width:100%; height:100%; filter: drop-shadow(0 0 28px rgba(159, 122, 234, 0.85));">
          <defs>
            <radialGradient id="glorHalo" cx="50%" cy="40%" r="70%">
              <stop offset="0%" stop-color="#FAF5FF"/>
              <stop offset="45%" stop-color="#A855F7" stop-opacity="0.5"/>
              <stop offset="100%" stop-color="#0F172A" stop-opacity="0"/>
            </radialGradient>
          </defs>
          <circle cx="100" cy="110" r="90" fill="url(#glorHalo)"/>
          <rect x="88" y="20" width="24" height="230" rx="8" fill="#F5C542" stroke="#B8860B" stroke-width="2.5"/>
          <rect x="35" y="65" width="130" height="24" rx="8" fill="#F5C542" stroke="#B8860B" stroke-width="2.5"/>
          <circle cx="100" cy="77" r="30" fill="#FAF5FF" stroke="#A855F7" stroke-width="2"/>
          <text x="100" y="86" text-anchor="middle" font-size="24">👑</text>
          <text x="100" y="48" text-anchor="middle" font-size="18">🌟</text>
          <rect x="55" y="225" width="90" height="24" rx="12" fill="rgba(15,23,42,0.9)" stroke="#C084FC" stroke-width="1.5"/>
          <text x="100" y="241" text-anchor="middle" fill="#E9D5FF" font-size="11" font-weight="bold">영광의 신비 성화</text>
        </svg>`;
    }
  }
"""

# Inject this function right before showCrucifixKissOverlay
if "getSacredArtForCurrentMystery()" not in text:
    kiss_idx = text.find('showCrucifixKissOverlay(onComplete)')
    if kiss_idx != -1:
        text = text[:kiss_idx] + art_generator_code + "\n\n  " + text[kiss_idx:]

# Ensure showCrucifixKissOverlay actually updates the target box with getSacredArtForCurrentMystery
target_render_code = """
    // 신비별 성화 렌더링
    const targetBox = document.getElementById("crucifixKissTarget");
    if (targetBox) {
      targetBox.innerHTML = this.getSacredArtForCurrentMystery();
    }
"""
if 'this.getSacredArtForCurrentMystery()' not in text:
    idx_overlay = text.find('showCrucifixKissOverlay(onComplete) {')
    if idx_overlay != -1:
        end_brace = text.find('{', idx_overlay) + 1
        text = text[:end_brace] + target_render_code + text[end_brace:]

with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text)

os.chdir("d:/부동산업무/antigravity/consult_diary")
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "feat: top header lang toggle, remove big lang card, dynamic 4-mystery sacred art v100"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("\n" + "="*50)
print("V100_LANG_AND_SACRED_ART_DEPLOYED_SUCCESSFULLY")
print("="*50)
