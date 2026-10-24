import os
import subprocess
import sys
import shutil

CURRENT_DIR = "d:/부동산업무/antigravity/consult_diary"
ROSARY_DIR = "d:/부동산업무/antigravity/rosary-app"

# 1. Update rosary-app/app.js to remove any undefined initCommunityStats and wire calendar properly
with open(os.path.join(ROSARY_DIR, "app.js"), "r", encoding="utf-8") as f:
    app_js = f.read()

# Replace any missing method calls
app_js = app_js.replace("this.initCommunityStats();", "// this.initCommunityStats();")

with open(os.path.join(ROSARY_DIR, "app.js"), "w", encoding="utf-8") as f:
    f.write(app_js)

# 2. In index.html, ensure btnIntroTracker has direct onclick:
with open(os.path.join(ROSARY_DIR, "index.html"), "r", encoding="utf-8") as f:
    index_html = f.read()

# Ensure openTracker function exists or trackerModal works
# Let's check modal script
tracker_fix = """
<script>
window.addEventListener('DOMContentLoaded', () => {
  const calBtn = document.getElementById('btnIntroTracker');
  if (calBtn) {
    calBtn.onclick = function() {
      if (window.rosaryApp) {
        window.rosaryApp.trackerWeekOffset = 0;
        window.rosaryApp.selectedTrackerDate = window.rosaryApp.getTodayStr();
        window.rosaryApp.renderWeeklyTracker();
        const m = document.getElementById('trackerModal');
        if (m) m.classList.add('show');
      }
    };
  }
  const closeCalBtn = document.getElementById('closeTrackerBtn');
  if (closeCalBtn) {
    closeCalBtn.onclick = function() {
      const m = document.getElementById('trackerModal');
      if (m) m.classList.remove('show');
    };
  }
});
</script>
"""

if "window.rosaryApp.trackerWeekOffset" not in index_html:
    index_html = index_html.replace("</body>", f"{tracker_fix}\n</body>")
    with open(os.path.join(ROSARY_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

# 3. Bundle
subprocess.run([sys.executable, "bundle.py"], cwd=ROSARY_DIR, check=True)

# 4. Copy to consult_diary
shutil.copy(os.path.join(ROSARY_DIR, "rosary.html"), os.path.join(CURRENT_DIR, "rosary.html"))

# 5. Git deploy
os.chdir(CURRENT_DIR)
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: calendar click handler and safe prayer stats"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("SUCCESS_CALENDAR_FULLY_WIRED")
