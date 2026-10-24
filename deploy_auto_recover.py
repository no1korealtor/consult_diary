import os
import subprocess
import sys
import shutil

ROSARY_DIR = "d:/부동산업무/antigravity/rosary-app"
CONSULT_DIR = "d:/부동산업무/antigravity/consult_diary"

with open(os.path.join(ROSARY_DIR, "index.html"), "r", encoding="utf-8") as f:
    html = f.read()

# Auto recovery script: reads any past history from localStorage keys and sums them up!
recovery_script = """
<script>
// [자동 복구 엔진] 기존에 바쳤던 모든 날짜의 기도 기록(History)을 자동으로 합산하여 내 봉헌 단수 복구
function autoRecoverRosaryStats() {
  try {
    let totalRecovered = 0;
    
    // 1. rosary_prayer_history_v1 스캔
    const histRaw = localStorage.getItem('rosary_prayer_history_v1');
    if (histRaw) {
      const hist = JSON.parse(histRaw);
      Object.keys(hist).forEach(k => {
        if (hist[k] && typeof hist[k].decades === 'number') {
          totalRecovered += hist[k].decades;
        }
      });
    }

    // 2. 다른 백업 키나 이전 키 스캔
    const oldKeys = ['rosary_history_v1', 'rosary_completed_decades_v1', 'rosary_history'];
    oldKeys.forEach(key => {
      const raw = localStorage.getItem(key);
      if (raw) {
        try {
          const parsed = JSON.parse(raw);
          if (typeof parsed === 'number') totalRecovered = Math.max(totalRecovered, parsed);
          else if (typeof parsed === 'object') {
            let sub = 0;
            Object.keys(parsed).forEach(k => {
              if (parsed[k] && parsed[k].decades) sub += parsed[k].decades;
            });
            totalRecovered = Math.max(totalRecovered, sub);
          }
        } catch(e){}
      }
    });

    // 3. 만약 복구된 총 단수가 0보다 크면 '내가 봉헌한 기도'와 '공동체'에 자동 반영!
    const commRaw = localStorage.getItem('rosary_community_v1');
    let commData = commRaw ? JSON.parse(commRaw) : { myTotal: 0, currentParish: '전국 교우 공동체' };
    
    if (totalRecovered > (commData.myTotal || 0)) {
      commData.myTotal = totalRecovered;
      localStorage.setItem('rosary_community_v1', JSON.stringify(commData));
    }

    // 화면 UI 업데이트
    const myEl = document.getElementById('myTotalDecades');
    const myRosesEl = document.getElementById('myTotalRoses');
    const commEl = document.getElementById('commTotalDecades');
    const commRosesEl = document.getElementById('commTotalRoses');

    const finalDecades = Math.max(totalRecovered, commData.myTotal || 0);
    if (myEl) myEl.textContent = finalDecades + '단';
    if (myRosesEl) myRosesEl.textContent = '(' + (finalDecades * 10) + '송이 🌹)';
    if (commEl && finalDecades > 0) commEl.textContent = (finalDecades + 128) + '단';
    if (commRosesEl && finalDecades > 0) commRosesEl.textContent = '(장미 ' + ((finalDecades + 128) * 10) + '송이 🌹)';

    console.log('[AutoRecover] Successfully recovered decades:', finalDecades);
  } catch (err) {
    console.warn('[AutoRecover] error:', err);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  autoRecoverRosaryStats();
  setTimeout(autoRecoverRosaryStats, 300);
});
</script>
"""

# Append recovery_script right before </body>
html = html.replace("</body>", f"{recovery_script}\n</body>")

with open(os.path.join(ROSARY_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

# Bundle
subprocess.run([sys.executable, "bundle.py"], cwd=ROSARY_DIR, check=True)

# Copy to consult_diary
shutil.copy(os.path.join(ROSARY_DIR, "rosary.html"), os.path.join(CONSULT_DIR, "rosary.html"))

# Git deploy
os.chdir(CONSULT_DIR)
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "feat: auto recover past prayer decades into community card"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("RECOVERY_SYSTEM_DEPLOYED_SUCCESSFULLY")
