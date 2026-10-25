import os
import subprocess
import shutil

ROSARY_DIR = "d:/부동산업무/antigravity/rosary-app"
CONSULT_DIR = "d:/부동산업무/antigravity/consult_diary"

with open(os.path.join(ROSARY_DIR, "index.html"), "r", encoding="utf-8") as f:
    html = f.read()

# Cut introResumeCard from current position and move it right after intro-hero-box (FIRST THING in the scroll body!)
resume_card_code = """        <!-- 0. 지난 기도 이어하기 카드 (진행 중인 기도가 있을 때 최상단 첫 번째 자리에 즉시 노출!) -->
        <div id="introResumeCard" class="intro-section-card resume-card" style="display: none; border: 1.5px solid var(--gold-primary); background: rgba(30, 41, 59, 0.95); box-shadow: 0 4px 18px rgba(243, 198, 105, 0.25); margin-bottom: 14px;">
          <div class="intro-card-header" style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 6px;">
              <span class="intro-card-icon" style="font-size: 1.15rem;">🕊️</span>
              <span id="introResumeTitle" class="intro-card-title" style="color: var(--gold-primary); font-weight: 800; font-size: 0.92rem;">지난 기도 이어하기</span>
            </div>
            <button type="button" id="btnIntroDismissResume" title="이어하기 기록 삭제" style="background: none; border: none; color: var(--text-muted); font-size: 0.75rem; cursor: pointer; padding: 2px 6px;">✕ 기록 삭제</button>
          </div>
          <div class="intro-resume-detail" style="margin: 8px 0 12px 0;">
            <span id="introResumeMystery" class="resume-mystery-text" style="font-size: 1rem; font-weight: 700; color: #FFF;">환희의 신비</span>
            <span id="introResumeStep" class="resume-step-text" style="font-size: 0.85rem; color: var(--gold-light);">제1단 · 성모송 3/10</span>
          </div>
          <button type="button" id="btnIntroContinue" class="intro-cta-btn resume" onclick="if(window.rosaryApp){window.rosaryApp.continuePrayer();}else{var iv=document.getElementById('introView');var pv=document.getElementById('prayerView');if(iv)iv.style.display='none';if(pv)pv.style.display='flex';}" style="width: 100%; height: 46px; font-size: 0.95rem; font-weight: 800; box-shadow: 0 4px 12px rgba(243,198,105,0.35);">
            <span>🕊️</span>
            <span id="introContinueText">이어서 계속 기도하기</span>
            <span style="font-size: 0.9rem; margin-left: 2px;">❯</span>
          </button>
        </div>
"""

# Remove old introResumeCard
old_start = html.find('<!-- 3. 지난 기도 이어하기 카드')
if old_start != -1:
    old_end = html.find('<!-- 4. 묵주기도 신비 선택 카드', old_start)
    html = html[:old_start] + html[old_end:]

# Insert right after intro-hero-box
hero_box_end = '<!-- 타이틀 & 날짜 헤더 -->\n        <div class="intro-hero-box">\n          <div class="intro-rose-emblem">🌹🕊️</div>\n          <h1 id="introHeroTitle" class="intro-hero-title">거룩한 묵주기도</h1>\n          <p id="introHeroDate" class="intro-hero-date">10월 14일 수요일</p>\n          <p id="introHeroQuote" class="intro-hero-quote">"성모님과 함께 바치는 거룩한 장미 화관"</p>\n        </div>'

if hero_box_end in html:
    html = html.replace(hero_box_end, hero_box_end + "\n\n" + resume_card_code)
else:
    # fallback find </div> right after intro-hero-box
    idx = html.find('id="introHeroQuote"')
    end_hero = html.find('</div>', idx) + 6
    html = html[:end_hero] + "\n\n" + resume_card_code + html[end_hero:]

with open(os.path.join(ROSARY_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

# Bundle
subprocess.run(["python", "bundle.py"], cwd=ROSARY_DIR, check=True)

# Copy to consult_diary
shutil.copy(os.path.join(ROSARY_DIR, "rosary.html"), os.path.join(CONSULT_DIR, "rosary.html"))

# Git push
os.chdir(CONSULT_DIR)
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "ux: elevate resume prayer card to absolute top before language and devotion"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("RESUME_CARD_TOP_DEPLOYED_SUCCESSFULLY")
