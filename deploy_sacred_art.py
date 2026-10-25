import os
import subprocess
import shutil

ROSARY_DIR = "d:/부동산업무/antigravity/rosary-app"
CONSULT_DIR = "d:/부동산업무/antigravity/consult_diary"

with open(os.path.join(ROSARY_DIR, "index.html"), "r", encoding="utf-8") as f:
    html = f.read()

# 4대 신비별 장엄하고 성스러운 가톨릭 클래식 명화 인라인 고화질 SVG & 그래픽
# 1. 환희의 신비: 수태고지 (성모영보 - 대천사 가브리엘과 성모님)
# 2. 빛의 신비: 주님의 세례 / 변모 (찬란한 천상의 빛)
# 3. 고통의 신비: 십자가 예수 수난 (San Damiano / 경건한 십자가)
# 4. 영광의 신비: 예수 부활과 성모 승천 (천상의 황금 영광)

# In index.html, replace the broken img tag inside kiss-crucifix-target with a majestic responsive Catholic Sacred Art SVG artwork!
old_target = """        <div class="kiss-crucifix-target" id="crucifixKissTarget" role="button" aria-label="십자가 친구하기">
          <!-- 거룩한 십자가 수난 성화 (축성된 성미술 원본 모티프) -->
          <img src="images/crucifix_sacred_art.webp" alt="거룩하신 우리 주 예수 그리스도의 십자가 수난 성화" class="sacred-crucifix-art-img" onerror="this.onerror=null; this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' viewBox=\\'0 0 100 140\\'><rect x=\\'44\\' y=\\'10\\' width=\\'12\\' height=\\'120\\' rx=\\'3\\' fill=\\'%23D4AF37\\' stroke=\\'%23854D0E\\' stroke-width=\\'2\\'/><rect x=\\'15\\' y=\\'35\\' width=\\'70\\' height=\\'12\\' rx=\\'3\\' fill=\\'%23D4AF37\\' stroke=\\'%23854D0E\\' stroke-width=\\'2\\'/><circle cx=\\'50\\' cy=\\'41\\' r=\\'8\\' fill=\\'%23FFFBEB\\' stroke=\\'%23D4AF37\\' stroke-width=\\'2\\'/></svg>';" />
          <div class="crucifix-art-halo"></div>
          <div class="crucifix-art-vignette"></div>
        </div>"""

new_target = """        <div class="kiss-crucifix-target" id="crucifixKissTarget" role="button" aria-label="십자가 친구하기" style="width: 220px; height: 310px; display: flex; align-items: center; justify-content: center; position: relative;">
          <!-- [4대 신비별 맞춤 성화 & 황금 십자가 컨테이너] -->
          <div id="sacredArtDisplayBox" style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
            <!-- JS에서 신비에 맞는 성화 SVG를 동적으로 렌더링 -->
          </div>
          <div class="crucifix-art-halo" style="position: absolute; width: 100%; height: 100%; pointer-events: none;"></div>
          <div class="crucifix-art-vignette" style="position: absolute; width: 100%; height: 100%; pointer-events: none;"></div>
        </div>"""

if old_target in html:
    html = html.replace(old_target, new_target)
    print("Replaced old_target successfully!")
else:
    # fallback find by id="crucifixKissTarget"
    idx = html.find('id="crucifixKissTarget"')
    end_box = html.find('</div>\n        <div class="kiss-guide-pill"', idx)
    html = html[:html.rfind('<div class="kiss-crucifix-target"', idx)] + new_target + html[end_box:]
    print("Replaced via fallback!")

with open(os.path.join(ROSARY_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

# Now update app.js to render the 4 mysteries sacred art dynamically!
with open(os.path.join(ROSARY_DIR, "app.js"), "r", encoding="utf-8") as f:
    app_js = f.read()

# Let's inspect where showCrucifixKissOverlay is in app.js
idx = app_js.find('showCrucifixKissOverlay(onComplete)')
end_fn = app_js.find('hideCrucifixKissOverlay', idx)

sacred_art_code = """  // 4대 신비별 성화 SVG 그래픽 생성기 (외부 이미지 다운로드 실패 없이 100% 로딩 보장)
  getSacredArtSvgForMystery(mysteryKey) {
    if (this.currentPrayerType === "divine_mercy") {
      // 자비의 예수님 성화 (붉은 빛과 흰 빛의 자비 광선)
      return `
        <svg viewBox="0 0 200 280" style="width:100%; height:100%; filter: drop-shadow(0 0 20px rgba(243, 198, 105, 0.7));">
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
          <!-- 자비의 예수님 형상 -->
          <circle cx="100" cy="55" r="22" fill="#FDE68A" stroke="#D97706" stroke-width="2"/>
          <circle cx="100" cy="55" r="30" fill="none" stroke="#F59E0B" stroke-width="1.5" stroke-dasharray="4,2"/>
          <path d="M85,75 Q100,70 115,75 L125,250 L75,250 Z" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5"/>
          <circle cx="100" cy="105" r="8" fill="#EF4444"/>
          <text x="100" y="272" text-anchor="middle" fill="#F3C669" font-size="11" font-weight="bold" letter-spacing="1">예수님, 저는 당신께 의탁합니다</text>
        </svg>
      `;
    }

    switch(mysteryKey) {
      case 'joyful':
        // 환희의 신비: 성모영보 & 평화의 비둘기와 백합
        return `
          <svg viewBox="0 0 200 280" style="width:100%; height:100%; filter: drop-shadow(0 0 22px rgba(72, 187, 120, 0.7));">
            <defs>
              <radialGradient id="joyHalo" cx="50%" cy="40%" r="65%">
                <stop offset="0%" stop-color="#FEF3C7"/>
                <stop offset="45%" stop-color="#6EE7B7" stop-opacity="0.4"/>
                <stop offset="100%" stop-color="#0F172A" stop-opacity="0"/>
              </radialGradient>
            </defs>
            <circle cx="100" cy="110" r="85" fill="url(#joyHalo)"/>
            <!-- 거룩한 황금 십자가 -->
            <rect x="88" y="20" width="24" height="230" rx="8" fill="#F5C542" stroke="#B8860B" stroke-width="2.5"/>
            <rect x="35" y="65" width="130" height="24" rx="8" fill="#F5C542" stroke="#B8860B" stroke-width="2.5"/>
            <!-- 순결한 백합 & 성모 마리아 영보 상징 -->
            <circle cx="100" cy="77" r="28" fill="#FFFDF0" stroke="#F5C542" stroke-width="2"/>
            <text x="100" y="83" text-anchor="middle" font-size="22">🌹</text>
            <!-- 천상 비둘기 -->
            <text x="100" y="48" text-anchor="middle" font-size="16">🕊️</text>
            <rect x="65" y="225" width="70" height="22" rx="11" fill="rgba(15,23,42,0.85)" stroke="#6EE7B7" stroke-width="1.5"/>
            <text x="100" y="240" text-anchor="middle" fill="#A7F3D0" font-size="10.5" font-weight="bold">환희의 신비 성화</text>
          </svg>
        `;
      case 'luminous':
        // 빛의 신비: 찬란한 천상의 빛과 거룩한 변모
        return `
          <svg viewBox="0 0 200 280" style="width:100%; height:100%; filter: drop-shadow(0 0 24px rgba(66, 153, 225, 0.8));">
            <defs>
              <radialGradient id="lumHalo" cx="50%" cy="40%" r="70%">
                <stop offset="0%" stop-color="#FFFFFF"/>
                <stop offset="40%" stop-color="#60A5FA" stop-opacity="0.5"/>
                <stop offset="100%" stop-color="#0F172A" stop-opacity="0"/>
              </radialGradient>
            </defs>
            <circle cx="100" cy="110" r="90" fill="url(#lumHalo)"/>
            <rect x="88" y="20" width="24" height="230" rx="8" fill="#F5C542" stroke="#B8860B" stroke-width="2.5"/>
            <rect x="35" y="65" width="130" height="24" rx="8" fill="#F5C542" stroke="#B8860B" stroke-width="2.5"/>
            <circle cx="100" cy="77" r="28" fill="#EFF6FF" stroke="#3B82F6" stroke-width="2"/>
            <text x="100" y="84" text-anchor="middle" font-size="22">💡</text>
            <text x="100" y="48" text-anchor="middle" font-size="16">✨</text>
            <rect x="65" y="225" width="70" height="22" rx="11" fill="rgba(15,23,42,0.85)" stroke="#93C5FD" stroke-width="1.5"/>
            <text x="100" y="240" text-anchor="middle" fill="#BFDBFE" font-size="10.5" font-weight="bold">빛의 신비 성화</text>
          </svg>
        `;
      case 'sorrowful':
        // 고통의 신비: 거룩한 십자가 수난 & 가시관
        return `
          <svg viewBox="0 0 200 280" style="width:100%; height:100%; filter: drop-shadow(0 0 24px rgba(229, 62, 62, 0.75));">
            <defs>
              <radialGradient id="sorHalo" cx="50%" cy="40%" r="65%">
                <stop offset="0%" stop-color="#FEE2E2"/>
                <stop offset="45%" stop-color="#EF4444" stop-opacity="0.4"/>
                <stop offset="100%" stop-color="#0F172A" stop-opacity="0"/>
              </radialGradient>
            </defs>
            <circle cx="100" cy="110" r="85" fill="url(#sorHalo)"/>
            <rect x="88" y="20" width="24" height="230" rx="8" fill="#D97706" stroke="#78350F" stroke-width="2.5"/>
            <rect x="35" y="65" width="130" height="24" rx="8" fill="#D97706" stroke="#78350F" stroke-width="2.5"/>
            <!-- 수난의 가시관 -->
            <circle cx="100" cy="77" r="28" fill="#450A0A" stroke="#EF4444" stroke-width="2"/>
            <text x="100" y="84" text-anchor="middle" font-size="22">✝️</text>
            <text x="100" y="48" text-anchor="middle" font-size="16">🩸</text>
            <rect x="65" y="225" width="70" height="22" rx="11" fill="rgba(15,23,42,0.85)" stroke="#F87171" stroke-width="1.5"/>
            <text x="100" y="240" text-anchor="middle" fill="#FECACA" font-size="10.5" font-weight="bold">고통의 신비 성화</text>
          </svg>
        `;
      case 'glorious':
      default:
        // 영광의 신비: 부활 승천 & 천상 모후의 관
        return `
          <svg viewBox="0 0 200 280" style="width:100%; height:100%; filter: drop-shadow(0 0 26px rgba(159, 122, 234, 0.8));">
            <defs>
              <radialGradient id="glorHalo" cx="50%" cy="40%" r="70%">
                <stop offset="0%" stop-color="#FAF5FF"/>
                <stop offset="45%" stop-color="#A855F7" stop-opacity="0.45"/>
                <stop offset="100%" stop-color="#0F172A" stop-opacity="0"/>
              </radialGradient>
            </defs>
            <circle cx="100" cy="110" r="90" fill="url(#glorHalo)"/>
            <rect x="88" y="20" width="24" height="230" rx="8" fill="#F5C542" stroke="#B8860B" stroke-width="2.5"/>
            <rect x="35" y="65" width="130" height="24" rx="8" fill="#F5C542" stroke="#B8860B" stroke-width="2.5"/>
            <circle cx="100" cy="77" r="28" fill="#FAF5FF" stroke="#A855F7" stroke-width="2"/>
            <text x="100" y="84" text-anchor="middle" font-size="22">👑</text>
            <text x="100" y="48" text-anchor="middle" font-size="16">🌟</text>
            <rect x="65" y="225" width="70" height="22" rx="11" fill="rgba(15,23,42,0.85)" stroke="#C084FC" stroke-width="1.5"/>
            <text x="100" y="240" text-anchor="middle" fill="#E9D5FF" font-size="10.5" font-weight="bold">영광의 신비 성화</text>
          </svg>
        `;
    }
  }
"""

new_show_kiss = """  showCrucifixKissOverlay(onComplete) {
    const overlay = this.dom.crucifixKissOverlay || document.getElementById("crucifixKissOverlay");
    if (!overlay) {
      if (onComplete) onComplete();
      return;
    }

    // 1. 신비별 성화 렌더링
    const box = document.getElementById("sacredArtDisplayBox");
    if (box) {
      box.innerHTML = this.getSacredArtSvgForMystery(this.currentMysteryKey);
    }

    overlay.style.display = "flex";
    overlay.classList.remove("kissed");
    overlay.classList.add("active");

    const target = this.dom.crucifixKissTarget || document.getElementById("crucifixKissTarget");
    const skipBtn = this.dom.btnCrucifixSkip || document.getElementById("btnCrucifixSkip");

    let isHandled = false;
    const handleKiss = (e) => {
      if (e && e.cancelable) e.preventDefault();
      if (isHandled) return;
      isHandled = true;

      if (this.settings.hapticEnabled && navigator.vibrate) {
        navigator.vibrate([40, 60, 80]);
      }
      if (this.settings.soundEnabled) {
        this.playRoseChime();
      }

      overlay.classList.add("kissed");
      setTimeout(() => {
        overlay.classList.remove("active");
        overlay.style.display = "none";
        if (onComplete) onComplete();
      }, 700);
    };

    if (target) {
      target.onclick = handleKiss;
      target.ontouchend = handleKiss;
    }
    if (skipBtn) {
      skipBtn.onclick = handleKiss;
    }
  }
"""

app_js = app_js[:idx] + sacred_art_code + "\n" + new_show_kiss + app_js[end_fn:]

with open(os.path.join(ROSARY_DIR, "app.js"), "w", encoding="utf-8") as f:
    f.write(app_js)

# Bundle
subprocess.run(["python", "bundle.py"], cwd=ROSARY_DIR, check=True)

# Copy to consult_diary
shutil.copy(os.path.join(ROSARY_DIR, "rosary.html"), os.path.join(CONSULT_DIR, "rosary.html"))

# Git push
os.chdir(CONSULT_DIR)
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "feat: 4 mysteries sacred art dynamic artwork for crucifix kiss"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("SACRED_ART_DEPLOYED_SUCCESSFULLY")
