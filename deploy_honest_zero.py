import os
import subprocess
import shutil

ROSARY_DIR = "d:/부동산업무/antigravity/rosary-app"
CONSULT_DIR = "d:/부동산업무/antigravity/consult_diary"

with open(os.path.join(ROSARY_DIR, "index.html"), "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update Intention Card and Empty State in HTML
new_card_markup = """
        <!-- [NEW] 함께 바치는 교우들의 지향 영역 -->
        <!-- A. 등록된 지향이 있을 때: 풍성한 카드 노출 -->
        <div id="introIntentionCard" class="intro-section-card intention-card" style="display: none; background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(243, 198, 105, 0.25); border-radius: var(--radius-md); padding: 14px 16px; margin-bottom: 12px; box-shadow: 0 4px 14px rgba(0,0,0,0.25);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 6px;">
              <span style="font-size: 1.05rem;">🕊️</span>
              <span style="font-weight: 700; font-size: 0.88rem; color: var(--gold-primary); letter-spacing: -0.2px;">함께 바치는 교우들의 지향</span>
            </div>
            <button type="button" id="btnOpenAddIntention" style="background: none; border: 1px solid rgba(243,198,105,0.3); color: var(--gold-light); font-size: 0.72rem; padding: 2px 8px; border-radius: 12px; cursor: pointer;">+ 새 지향 올리기</button>
          </div>
          
          <p id="intentionBodyText" style="font-size: 0.92rem; color: #F8FAFC; line-height: 1.55; margin: 0 0 10px 0; word-break: keep-all; font-style: italic; background: rgba(15, 23, 42, 0.5); padding: 10px 12px; border-radius: 8px; border-left: 3px solid var(--gold-primary);">
            ""
          </p>

          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span id="intentionPrayerCountLabel" style="font-size: 0.78rem; color: var(--text-secondary); display: flex; align-items: center; gap: 4px;">
              🌹 <span id="intentionCountNum" style="color: var(--gold-light); font-weight: 700;">0</span>명의 교우가 함께 기도 중
            </span>
            <button type="button" id="btnJoinIntention" style="background: linear-gradient(135deg, #B8860B, #D4AF37); color: #0C111D; border: none; font-size: 0.8rem; font-weight: 800; padding: 6px 14px; border-radius: 20px; cursor: pointer; display: flex; align-items: center; gap: 4px; box-shadow: 0 2px 8px rgba(243,198,105,0.3); transition: transform 0.15s ease;">
              <span>🌹</span>
              <span id="btnJoinIntentionText">함께 기도하겠습니다</span>
            </button>
          </div>
        </div>

        <!-- B. 등록된 지향이 없을 때: 단정하고 거슬리지 않는 한 줄 링크 (지향 올리기 항상 가능) -->
        <div id="introIntentionEmptyPrompt" style="display: flex; justify-content: space-between; align-items: center; background: rgba(30, 41, 59, 0.35); border: 1px dashed rgba(243, 198, 105, 0.2); border-radius: var(--radius-md); padding: 10px 14px; margin-bottom: 12px;">
          <span style="font-size: 0.78rem; color: var(--text-secondary); display: flex; align-items: center; gap: 6px;">
            <span>🕊️</span>
            <span>성모님과 교우들에게 청할 지향이 있으신가요?</span>
          </span>
          <button type="button" id="btnOpenAddIntentionEmpty" style="background: rgba(243,198,105,0.12); border: 1px solid rgba(243,198,105,0.35); color: var(--gold-primary); font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 12px; cursor: pointer;">
            + 지향 올리기
          </button>
        </div>
"""

# Replace old introIntentionCard in html
old_card_marker = '<!-- [NEW] 함께 바치는 교우들의 지향 카드'
old_card_end = '<!-- 6. 주간 기록 미니 현황 카드 -->'

if old_card_marker in html:
    idx_start = html.find(old_card_marker)
    idx_end = html.find(old_card_end)
    html = html[:idx_start] + new_card_markup + "\n        " + html[idx_end:]

# 2. Update Javascript Logic to start from 0 honestly
new_js_logic = """
// ==========================================
// [교우 기도 지향 관리 엔진 - 정직한 카운트 & 스마트 노출]
// ==========================================
(function() {
  const STORAGE_KEY = 'rosary_community_intention_v1';
  const JOINED_KEY = 'rosary_joined_intention_id_v1';

  function getStoredIntention() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw || raw === 'NONE') return null;
      const parsed = JSON.parse(raw);
      return (parsed && parsed.active && parsed.text) ? parsed : null;
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
    const emptyPrompt = document.getElementById('introIntentionEmptyPrompt');
    if (!card || !emptyPrompt) return;

    const data = getStoredIntention();
    if (!data || !data.text || !data.active) {
      // 등록된 지향이 없을 때: 큰 카드는 숨기고 단정한 한 줄 링크만 표시!
      card.style.display = 'none';
      emptyPrompt.style.display = 'flex';
      return;
    }

    // 등록된 지향이 있을 때: 큰 카드 노출 및 한 줄 링크 숨김
    card.style.display = 'block';
    emptyPrompt.style.display = 'none';

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

    // 내가 눌렀는지 확인
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
          // 이미 누름 -> 취소
          data.count = Math.max(0, (data.count || 1) - 1);
          localStorage.removeItem(JOINED_KEY);
        } else {
          // 새로 누름 -> 정직하게 1명 증가
          data.count = (data.count || 0) + 1;
          localStorage.setItem(JOINED_KEY, data.id);
          if (navigator.vibrate) navigator.vibrate([30, 40]);
        }

        saveStoredIntention(data);
        renderIntentionCard();
      };
    }

    // 2. 모달 열기 (카드 내 버튼 및 한줄 링크 버튼 둘 다 연결)
    const openBtn1 = document.getElementById('btnOpenAddIntention');
    const openBtn2 = document.getElementById('btnOpenAddIntentionEmpty');
    const modal = document.getElementById('intentionModal');
    const dismissBtn = document.getElementById('btnDismissIntentionModal');
    const submitBtn = document.getElementById('btnSubmitIntention');
    const inputTxt = document.getElementById('inputIntentionText');
    const inputAuthor = document.getElementById('inputIntentionAuthor');

    const handleOpen = function() {
      if (inputTxt) inputTxt.value = '';
      if (inputAuthor) inputAuthor.value = '';
      if (modal) modal.classList.add('show');
    };

    if (openBtn1) openBtn1.onclick = handleOpen;
    if (openBtn2) openBtn2.onclick = handleOpen;

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
        // 정직하게 0부터 시작!
        const newIntention = {
          id: 'int_' + Date.now(),
          text: txt,
          author: author,
          count: 0,
          createdAt: Date.now(),
          active: true
        };

        saveStoredIntention(newIntention);
        localStorage.removeItem(JOINED_KEY);
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

# Replace intention script
script_start = html.find("// ==========================================\n// [교우 기도 지향 관리 엔진")
if script_start != -1:
    script_end = html.find("</script>", script_start)
    html = html[:script_start] + new_js_logic + html[script_end:]

with open(os.path.join(ROSARY_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

# Bundle
subprocess.run(["python", "bundle.py"], cwd=ROSARY_DIR, check=True)

# Copy to consult_diary
shutil.copy(os.path.join(ROSARY_DIR, "rosary.html"), os.path.join(CONSULT_DIR, "rosary.html"))

# Git push
os.chdir(CONSULT_DIR)
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "feat: start intention count honestly from 0 with minimal empty prompt"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("HONEST_ZERO_INTENTION_DEPLOYED_SUCCESSFULLY")
