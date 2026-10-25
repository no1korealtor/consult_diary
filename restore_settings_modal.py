import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

has_settings_modal = 'id="settingsModal"' in text
print("Has settingsModal in HTML?", has_settings_modal)

if not has_settings_modal:
    # Need to restore settingsModal!
    settings_modal_html = """
    <!-- 8. 설정 모달 바텀시트 -->
    <div id="settingsModal" class="modal-backdrop">
      <div class="bottom-sheet">
        <div class="sheet-handle"></div>
        <div class="sheet-title-row" style="display: flex; align-items: center; justify-content: space-between;">
          <h3 class="sheet-title" style="margin: 0;">설정</h3>
          <button type="button" id="closeSettingsBtn" class="tracker-close-btn" onclick="directCloseSettings();" aria-label="닫기">✕</button>
        </div>

        <div class="settings-content" style="max-height: 70vh; overflow-y: auto;">
          <!-- 글자 크기 -->
          <div class="setting-row">
            <span class="setting-label">글자 크기</span>
            <div class="font-size-controls">
              <button type="button" id="fontSmallerBtn" class="font-btn">가-</button>
              <button type="button" id="fontBiggerBtn" class="font-btn">가+</button>
            </div>
          </div>

          <!-- 기도 소리 (종소리) -->
          <div class="setting-row">
            <span class="setting-label">기도 알림 소리 (종소리)</span>
            <label class="toggle-switch">
              <input type="checkbox" id="soundToggle">
              <span class="toggle-slider"></span>
            </label>
          </div>

          <!-- 진동 (햅틱) 피드백 -->
          <div class="setting-row">
            <span class="setting-label">진동 피드백</span>
            <label class="toggle-switch">
              <input type="checkbox" id="hapticToggle" checked>
              <span class="toggle-slider"></span>
            </label>
          </div>

          <!-- 구원을 비는 기도 (구원송) -->
          <div class="setting-row">
            <div>
              <div class="setting-label">구원을 비는 기도 (구원송)</div>
              <small style="color: var(--text-muted); font-size: 0.74rem;">각 단 영광송 뒤에 바침</small>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" id="settingsFatimaToggle" checked>
              <span class="toggle-slider"></span>
            </label>
          </div>

          <!-- 장미 꽃피움 연출 효과 -->
          <div class="setting-row">
            <div>
              <div class="setting-label">성모송 장미 꽃피움 연출</div>
              <small style="color: var(--text-muted); font-size: 0.74rem;">성모송마다 피어나는 은총의 장미</small>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" id="roseBloomToggle" checked>
              <span class="toggle-slider"></span>
            </label>
          </div>

          <!-- 묵주알 모양 -->
          <div class="setting-row" style="flex-direction: column; align-items: flex-start; gap: 8px;">
            <span class="setting-label">묵주알 모양 선택</span>
            <div style="display: flex; gap: 8px; width: 100%;">
              <button type="button" id="btnStyleWood" class="action-pill-btn active" style="flex: 1; height: 36px; font-size: 0.8rem;">원목 묵주</button>
              <button type="button" id="btnStyleRose" class="action-pill-btn" style="flex: 1; height: 36px; font-size: 0.8rem;">장미 화관</button>
              <button type="button" id="btnStyleClassic" class="action-pill-btn" style="flex: 1; height: 36px; font-size: 0.8rem;">원형 알</button>
            </div>
          </div>

          <!-- 기도 언어 -->
          <div class="setting-row" style="flex-direction: column; align-items: flex-start; gap: 8px;">
            <span class="setting-label">기도 언어 (Language)</span>
            <div style="display: flex; gap: 8px; width: 100%;">
              <button type="button" id="btnLangKo" class="action-pill-btn active" style="flex: 1; height: 36px; font-size: 0.8rem;">한국어</button>
              <button type="button" id="btnLangEn" class="action-pill-btn" style="flex: 1; height: 36px; font-size: 0.8rem;">English</button>
            </div>
          </div>

          <!-- 기도 기록 백업 및 복원 -->
          <div class="setting-row" style="padding-top: 14px;">
            <div>
              <div class="setting-label">💾 기도 기록 백업 및 복원</div>
              <small style="color: var(--text-muted); font-size: 0.74rem;">소중한 기도 기록을 안전하게 보관</small>
            </div>
            <button type="button" id="btnSettingsOpenBackup" class="action-pill-btn gold" style="height: 32px; font-size: 0.78rem; padding: 0 12px;">백업/복원</button>
          </div>

          <!-- 바로가기 추가 안내 -->
          <div class="setting-row">
            <div>
              <div class="setting-label">📲 바탕화면에 바로가기 추가</div>
              <small style="color: var(--text-muted); font-size: 0.74rem;">홈 화면에서 바로 실행</small>
            </div>
            <button type="button" id="btnSettingsInstall" class="action-pill-btn" style="height: 32px; font-size: 0.78rem; padding: 0 12px;">안내</button>
          </div>

          <!-- 기도의 유래와 은총 -->
          <div class="setting-row">
            <div>
              <div id="settingHistoryLabel" class="setting-label">📖 기도의 유래와 은총</div>
              <small id="settingHistorySub" style="color: var(--text-muted); font-size: 0.74rem;">묵주기도 및 자비의 기도 역사와 약속된 은총</small>
            </div>
            <button type="button" id="btnSettingsOpenHistory" class="action-pill-btn" style="height: 32px; font-size: 0.78rem; padding: 0 12px;">보기</button>
          </div>

          <!-- 개발자 응원하기 -->
          <div class="setting-row">
            <div>
              <div id="settingDonationLabel" class="setting-label">☕ 따뜻한 차 한 잔 후원하기</div>
              <small id="settingDonationSub" style="color: var(--text-muted); font-size: 0.74rem;">광고 없는 무료 기도 앱 개발자 응원하기</small>
            </div>
            <button type="button" id="btnSettingsOpenDonation" class="action-pill-btn gold" style="height: 32px; font-size: 0.78rem; padding: 0 12px;">응원하기</button>
          </div>

          <div style="margin-top: 14px;">
            <button type="button" onclick="directCloseSettings();" class="action-pill-btn" style="width: 100%; height: 42px; font-size: 0.9rem;">
              닫기
            </button>
          </div>
        </div>
      </div>
    </div>
"""
    # Insert before mysteryModal
    target_pos = text.find('<div id="mysteryModal"')
    if target_pos != -1:
        text = text[:target_pos] + settings_modal_html + "\n\n" + text[target_pos:]
        print("Restored settingsModal before mysteryModal!")
    else:
        # insert before </section> or trackerModal
        target_pos = text.find('<div id="trackerModal"')
        text = text[:target_pos] + settings_modal_html + "\n\n" + text[target_pos:]
        print("Restored settingsModal before trackerModal!")

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text)

print("HTML check and update complete!")
