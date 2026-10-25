import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

has_method = "getSacredArtSvgForMystery" in text
print("Has getSacredArtSvgForMystery?", has_method)

# Let's inspect RosaryApp prototype or definition
art_method = """
  getSacredArtSvgForMystery(mysteryKey) {
    // 4대 신비별 거룩한 벡터 성화 SVG
    switch (mysteryKey) {
      case 'luminous': // 빛의 신비 - 주님의 세례와 천상 비둘기 & 빛살
        return `
          <svg viewBox="0 0 200 280" width="100%" height="100%">
            <defs>
              <linearGradient id="luminousSky" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#1E3A8A"/>
                <stop offset="50%" stop-color="#0284C7"/>
                <stop offset="100%" stop-color="#38BDF8"/>
              </linearGradient>
              <radialGradient id="heavenLight" cx="50%" cy="15%" r="60%">
                <stop offset="0%" stop-color="#FFFBEB" stop-opacity="1"/>
                <stop offset="50%" stop-color="#FDE047" stop-opacity="0.6"/>
                <stop offset="100%" stop-color="#0284C7" stop-opacity="0"/>
              </radialGradient>
            </defs>
            <rect width="200" height="280" rx="8" fill="url(#luminousSky)"/>
            <rect width="200" height="280" rx="8" fill="url(#heavenLight)"/>
            <!-- 천상 성령의 비둘기 -->
            <path d="M100 40 Q90 55 75 50 Q85 62 100 68 Q115 62 125 50 Q110 55 100 40 Z" fill="#FFFFFF" filter="drop-shadow(0 0 8px #FFF)"/>
            <circle cx="100" cy="50" r="18" fill="none" stroke="#FEF08A" stroke-width="1.5" stroke-dasharray="3,3"/>
            <!-- 요르단 강 물결 -->
            <path d="M0 220 Q50 210 100 220 T200 220 L200 280 L0 280 Z" fill="#0369A1" opacity="0.85"/>
            <path d="M0 235 Q50 225 100 235 T200 235 L200 280 L0 280 Z" fill="#0284C7" opacity="0.9"/>
            <text x="100" y="260" text-anchor="middle" fill="#FEF08A" font-size="12" font-weight="700" letter-spacing="1">빛의 신비 (LUMINOUS)</text>
          </svg>
        `;
      case 'sorrowful': // 고통의 신비 - 갈바리아 십자가 구원
        return `
          <svg viewBox="0 0 200 280" width="100%" height="100%">
            <defs>
              <linearGradient id="sorrowSky" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#18181B"/>
                <stop offset="60%" stop-color="#450A0A"/>
                <stop offset="100%" stop-color="#7F1D1D"/>
              </linearGradient>
            </defs>
            <rect width="200" height="280" rx="8" fill="url(#sorrowSky)"/>
            <!-- 붉은 노을 빛살 -->
            <path d="M100 120 L30 0 L170 0 Z" fill="rgba(239, 68, 68, 0.15)"/>
            <!-- 갈바리아 언덕 -->
            <path d="M0 230 Q100 190 200 230 L200 280 L0 280 Z" fill="#09090B"/>
            <!-- 주님의 구원 십자가 -->
            <rect x="94" y="60" width="12" height="150" rx="2" fill="#E2E8F0" stroke="#991B1B" stroke-width="1.5"/>
            <rect x="65" y="95" width="70" height="12" rx="2" fill="#E2E8F0" stroke="#991B1B" stroke-width="1.5"/>
            <!-- 가시관 -->
            <ellipse cx="100" cy="92" rx="10" ry="5" fill="none" stroke="#DC2626" stroke-width="2"/>
            <text x="100" y="260" text-anchor="middle" fill="#FCA5A5" font-size="12" font-weight="700" letter-spacing="1">고통의 신비 (SORROWFUL)</text>
          </svg>
        `;
      case 'glorious': // 영광의 신비 - 찬란한 부활과 영광
        return `
          <svg viewBox="0 0 200 280" width="100%" height="100%">
            <defs>
              <linearGradient id="gloriousSky" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#312E81"/>
                <stop offset="60%" stop-color="#5B21B6"/>
                <stop offset="100%" stop-color="#7C3AED"/>
              </linearGradient>
              <radialGradient id="gloryAura" cx="50%" cy="40%" r="50%">
                <stop offset="0%" stop-color="#FEF08A"/>
                <stop offset="50%" stop-color="#EAB308" stop-opacity="0.8"/>
                <stop offset="100%" stop-color="#7C3AED" stop-opacity="0"/>
              </radialGradient>
            </defs>
            <rect width="200" height="280" rx="8" fill="url(#gloriousSky)"/>
            <rect width="200" height="280" rx="8" fill="url(#gloryAura)"/>
            <!-- 부활 승리의 깃발 십자가 -->
            <line x1="100" y1="50" x2="100" y2="200" stroke="#FEF08A" stroke-width="3"/>
            <line x1="80" y1="80" x2="120" y2="80" stroke="#FEF08A" stroke-width="3"/>
            <polygon points="100,60 135,75 100,90" fill="#EF4444"/>
            <!-- 승리의 별빛무리 -->
            <circle cx="100" cy="110" r="35" fill="none" stroke="#FEF08A" stroke-width="1.5" stroke-dasharray="4,4"/>
            <text x="100" y="260" text-anchor="middle" fill="#FDE047" font-size="12" font-weight="700" letter-spacing="1">영광의 신비 (GLORIOUS)</text>
          </svg>
        `;
      default: // 환희의 신비 (joyful) & 기본 - 성모 영보와 장미
        return `
          <svg viewBox="0 0 200 280" width="100%" height="100%">
            <defs>
              <linearGradient id="joyfulSky" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#064E3B"/>
                <stop offset="60%" stop-color="#047857"/>
                <stop offset="100%" stop-color="#10B981"/>
              </linearGradient>
              <radialGradient id="roseGlow" cx="50%" cy="45%" r="45%">
                <stop offset="0%" stop-color="#FEE2E2"/>
                <stop offset="60%" stop-color="#F43F5E" stop-opacity="0.7"/>
                <stop offset="100%" stop-color="#047857" stop-opacity="0"/>
              </radialGradient>
            </defs>
            <rect width="200" height="280" rx="8" fill="url(#joyfulSky)"/>
            <rect width="200" height="280" rx="8" fill="url(#roseGlow)"/>
            <!-- 성스러운 장미 화관 심볼 -->
            <circle cx="100" cy="120" r="42" fill="none" stroke="#FDE047" stroke-width="2" stroke-dasharray="5,3"/>
            <text x="100" y="130" text-anchor="middle" font-size="32">🌹</text>
            <text x="100" y="260" text-anchor="middle" fill="#FEF08A" font-size="12" font-weight="700" letter-spacing="1">환희의 신비 (JOYFUL)</text>
          </svg>
        `;
    }
  }
"""

if not has_method:
    # Add getSacredArtSvgForMystery right before showCrucifixKissOverlay
    idx_target = text.find("showCrucifixKissOverlay(onComplete)")
    if idx_target != -1:
        text = text[:idx_target] + art_method + "\n  " + text[idx_target:]
        print("Added getSacredArtSvgForMystery method to RosaryApp!")

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Check completed!")
