import os
import subprocess
import sys
import shutil

ROSARY_DIR = "d:/부동산업무/antigravity/rosary-app"
CONSULT_DIR = "d:/부동산업무/antigravity/consult_diary"

with open(os.path.join(ROSARY_DIR, "index.html"), "r", encoding="utf-8") as f:
    html = f.read()

# 1. Add Community Intention Card in HTML (right under community-stats-card)
intention_card_html = """
        <!-- [NEW] 함께 바치는 교우들의 지향 카드 (지향이 등록되어 있을 때만 우아하게 노출, 없으면 완전 숨김) -->
        <div id="introIntentionCard" class="intro-section-card intention-card" style="display: none; background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(243, 198, 105, 0.25); border-radius: var(--radius-md); padding: 14px 16px; margin-bottom: 12px; box-shadow: 0 4px 14px rgba(0,0,0,0.25);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 6px;">
              <span style="font-size: 1.05rem;">🕊️</span>
              <span style="font-weight: 700; font-size: 0.88rem; color: var(--gold-primary); letter-spacing: -0.2px;">함께 바치는 교우들의 지향</span>
            </div>
            <button type="button" id="btnOpenAddIntention" style="background: none; border: 1px solid rgba(243,198,105,0.3); color: var(--gold-light); font-size: 0.72rem; padding: 2px 8px; border-radius: 12px; cursor: pointer;">+ 내 지향 올리기</button>
          </div>
          
          <p id="intentionBodyText" style="font-size: 0.92rem; color: #F8FAFC; line-height: 1.55; margin: 0 0 10px 0; word-break: keep-all; font-style: italic; background: rgba(15, 23, 42, 0.5); padding: 10px 12px; border-radius: 8px; border-left: 3px solid var(--gold-primary);">
            "수술을 앞둔 어머니(데레사)의 평안과 쾌유를 위해 기도 부탁드립니다."
          </p>

          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span id="intentionPrayerCountLabel" style="font-size: 0.78rem; color: var(--text-secondary); display: flex; align-items: center; gap: 4px;">
              🌹 <span id="intentionCountNum" style="color: var(--gold-light); font-weight: 700;">42</span>명의 교우가 함께 기도 중
            </span>
            <button type="button" id="btnJoinIntention" style="background: linear-gradient(135deg, #B8860B, #D4AF37); color: #0C111D; border: none; font-size: 0.8rem; font-weight: 800; padding: 6px 14px; border-radius: 20px; cursor: pointer; display: flex; align-items: center; gap: 4px; box-shadow: 0 2px 8px rgba(243,198,105,0.3); transition: transform 0.15s ease;">
              <span>🌹</span>
              <span id="btnJoinIntentionText">함께 기도하겠습니다</span>
            </button>
          </div>
        </div>
"""

# Place it right after introCommunityCard
target_card_end = '<!-- 6. 주간 기록 미니 현황 카드 -->'
if "id=\"introIntentionCard\"" not in html:
    html = html.replace(target_card_end, intention_card_html + "\n" + target_card_end)

# 2. Add Intention Modal (for adding intention)
intention_modal_html = """
    <!-- 13. 교우 지향 등록 모달 바텀시트 -->
    <div id="intentionModal" class="modal-backdrop">
      <div class="bottom-sheet" style="max-width: 440px;">
        <div class="sheet-handle"></div>
        <div class="sheet-title" style="display: flex; align-items: center; justify-content: center; gap: 8px;">
          <span>🕊️</span> <span>함께 나눌 기도 지향 올리기</span>
        </div>
        
        <div style="padding: 10px 4px 16px;">
          <p style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 12px; text-align: center;">
            전국의 교우들과 성모님 품에 함께 봉헌하고 싶은 지향을 1~2문장으로 정갈하게 남겨주세요.
          </p>

          <textarea id="inputIntentionText" maxlength="120" placeholder="예: 가족의 건강과 냉담 중인 자녀의 평안을 위해 함께 묵주기도 부탁드립니다." style="width: 100%; height: 90px; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(243, 198, 105, 0.3); border-radius: 8px; color: #FFF; padding: 10px; font-size: 0.9rem; resize: none; box-sizing: border-box; font-family: inherit; margin-bottom: 10px;"></textarea>
          
          <div style="display: flex; gap: 8px; margin-bottom: 14px;">
            <input type="text" id="inputIntentionAuthor" maxlength="12" placeholder="작성자 (예: 익명, 마리아, 베드로)" style="flex: 1; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 8px; color: #FFF; padding: 8px 10px; font-size: 0.82rem; box-sizing: border-box; font-family: inherit;">
          </div>

          <div style="display: flex; gap: 8px;">
            <button type="button" id="btnDismissIntentionModal" class="action-pill-btn" style="flex: 1; height: 42px; font-size: 0.88rem;">취소</button>
            <button type="button" id="btnSubmitIntention" class="action-pill-btn gold" style="flex: 2; height: 42px; font-size: 0.88rem; font-weight: 800;">🕊️ 지향 봉헌하기</button>
          </div>
        </div>
      </div>
    </div>
"""

if "id=\"intentionModal\"" not in html:
    html = html.replace('<div id="donationModal"', intention_modal_html + "\n    <div id=\"donationModal\"")

# 3. Add Intention Logic in JS
intention_js = """
// ==========================================
// [교우 기도 지향 관리 엔진]
// 지향이 있을 때만 단정하게 표시, 없으면 완전 숨김
// ==========================================
(function() {
  const STORAGE_KEY = 'rosary_community_intention_v1';
  const JOINED_KEY = 'rosary_joined_intention_id_v1';

  // 기본 샘플 지향 (첫 사용자 경험 제공용, 사용자가 삭제하거나 비우면 완전히 사라짐)
  const defaultIntention = {
    id: 'int_sample_01',
    text: '수술을 앞둔 어머니(데레사)의 평안과 쾌유를 위해 기도 부탁드립니다.',
    author: '익명의 교우',
    count: 42,
    createdAt: Date.now(),
    active: true
  };

  function getStoredIntention() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw === 'NONE') return null; // 명시적으로 비어있는 상태
      if (!raw) return defaultIntention; // 최초 1회만 노출
      const parsed = JSON.parse(raw);
      return (parsed && parsed.active) ? parsed : null;
    } catch(e) {
      return null;
    }
  }

  function saveStoredIntention(item) {
    try {
      if (!item) {
        localStorage.setItem(STORAGE_KEY, 'NONE');
      } else {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(item));
      }
    } catch(e){}
  }

  function renderIntentionCard() {
    const card = document.getElementById('introIntentionCard');
    if (!card) return;

    const data = getStoredIntention();
    if (!data || !data.text || !data.active) {
      // 등록된 지향이 전혀 없을 때 거슬리지 않도록 완전 숨김!
      card.style.display = 'none';
      return;
    }

    // 지향이 있을 때만 은은하게 노출
    card.style.display = 'block';

    const bodyEl = document.getElementById('intentionBodyText');
    const countEl = document.getElementById('intentionCountNum');
    const joinBtn = document.getElementById('btnJoinIntention');
    const joinText = document.getElementById('btnJoinIntentionText');

    if (bodyEl) {
      bodyEl.textContent = `"${data.text}"`;
    }
    if (countEl) {
      countEl.textContent = data.count || 0;
    }

    // 이미 내가 '함께 기도하겠습니다'를 눌렀는지 확인
    const joinedId = localStorage.getItem(JOINED_KEY);
    const hasJoined = joinedId === data.id;

    if (joinBtn && joinText) {
      if (hasJoined) {
        joinBtn.style.background = 'rgba(243, 198, 105, 0.18)';
        joinBtn.style.color = '#F3C669';
        joinBtn.style.border = '1px solid rgba(243, 198, 105, 0.4)';
        joinText.textContent = '함께 기도하는 중 🙏';
      } else {
        joinBtn.style.background = 'linear-gradient(135deg, #B8860B, #D4AF37)';
        joinBtn.style.color = '#0C111D';
        joinBtn.style.border = 'none';
        joinText.textContent = '함께 기도하겠습니다';
      }
    }
  }

  function wireEvents() {
    // 1. '함께 기도하겠습니다' 버튼
    const joinBtn = document.getElementById('btnJoinIntention');
    if (joinBtn) {
      joinBtn.onclick = function() {
        const data = getStoredIntention();
        if (!data) return;

        const joinedId = localStorage.getItem(JOINED_KEY);
        if (joinedId === data.id) {
          // 이미 누름 -> 토글 해제
          data.count = Math.max(0, (data.count || 1) - 1);
          localStorage.removeItem(JOINED_KEY);
        } else {
          // 새로 누름 -> 카운트 증가 + 토스트 피드백
          data.count = (data.count || 0) + 1;
          localStorage.setItem(JOINED_KEY, data.id);
          
          if (navigator.vibrate) navigator.vibrate([30, 40]);
        }

        saveStoredIntention(data);
        renderIntentionCard();
      };
    }

    // 2. 모달 열기/닫기
    const openBtn = document.getElementById('btnOpenAddIntention');
    const modal = document.getElementById('intentionModal');
    const dismissBtn = document.getElementById('btnDismissIntentionModal');
    const submitBtn = document.getElementById('btnSubmitIntention');
    const inputTxt = document.getElementById('inputIntentionText');
    const inputAuthor = document.getElementById('inputIntentionAuthor');

    if (openBtn && modal) {
      openBtn.onclick = function() {
        if (inputTxt) inputTxt.value = '';
        if (inputAuthor) inputAuthor.value = '';
        modal.classList.add('show');
      };
    }

    if (dismissBtn && modal) {
      dismissBtn.onclick = function() {
        modal.classList.remove('show');
      };
    }

    if (submitBtn && modal && inputTxt) {
      submitBtn.onclick = function() {
        const txt = (inputTxt.value || '').trim();
        if (!txt) {
          alert('기도 지향 내용을 한 문장 이상 입력해 주세요.');
          return;
        }

        const author = (inputAuthor.value || '').trim() || '익명의 교우';
        const newIntention = {
          id: 'int_' + Date.now(),
          text: txt,
          author: author,
          count: 1,
          createdAt: Date.now(),
          active: true
        };

        saveStoredIntention(newIntention);
        localStorage.setItem(JOINED_KEY, newIntention.id); // 올린 사람은 자동 참여
        modal.classList.remove('show');
        renderIntentionCard();
      };
    }
  }

  // 초기 렌더링
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      wireEvents();
      renderIntentionCard();
    });
  } else {
    wireEvents();
    renderIntentionCard();
  }
})();
"""

# Append intention_js right before </body>
html = html.replace("</body>", f"<script>\n{intention_js}\n</script>\n</body>")

with open(os.path.join(ROSARY_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

# Bundle
subprocess.run([sys.executable, "bundle.py"], cwd=ROSARY_DIR, check=True)

# Copy to consult_diary
shutil.copy(os.path.join(ROSARY_DIR, "rosary.html"), os.path.join(CONSULT_DIR, "rosary.html"))

# Git push
os.chdir(CONSULT_DIR)
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "feat: prayer intention card with auto-hide and pray-together like button"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("INTENTION_FEATURE_DEPLOYED_SUCCESSFULLY")
