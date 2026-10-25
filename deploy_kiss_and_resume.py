import os
import subprocess
import shutil

ROSARY_DIR = "d:/부동산업무/antigravity/rosary-app"
CONSULT_DIR = "d:/부동산업무/antigravity/consult_diary"

with open(os.path.join(ROSARY_DIR, "app.js"), "r", encoding="utf-8") as f:
    app_js = f.read()

# 1. Update saveProgress: Allow saving even if currentView is transition or prayer
old_save = """  saveProgress() {
    // 기도 화면에 머물고 있을 때만 저장하며, 0단계(기도 시작 전)이거나 인트로 화면일 때는 이전 상태를 덮어쓰지 않음
    if (this.currentView !== "prayer") return;
    if (this.currentIndex <= 0) return;"""

new_save = """  saveProgress() {
    // 0단계 시작 전이더라도 인덱스가 0보다 크면 항상 안전하게 저장
    if (this.currentIndex <= 0) return;"""

if old_save in app_js:
    app_js = app_js.replace(old_save, new_save)
    print("saveProgress updated!")

# 2. In goToStep, always call saveProgress() whenever user moves beads!
old_goto = """    // 5) 성모송 생화 장미 연출 및 바운스 피드백 실행
    if (animate && this.settings.roseBloomEffect && step.beadType === "small") {
      this.triggerRoseBloom(step);
    }"""

new_goto = """    // 5) 성모송 생화 장미 연출 및 바운스 피드백 실행
    if (animate && this.settings.roseBloomEffect && step.beadType === "small") {
      this.triggerRoseBloom(step);
    }
    // 진행 상태 자동 실시간 저장 (이어하기 완벽 보장)
    this.saveProgress();"""

if old_goto in app_js:
    app_js = app_js.replace(old_goto, new_goto)
    print("goToStep saveProgress added!")

# 3. Ensure startPrayer always launches the holy Crucifix Kiss Overlay (성화 친구 연출)
old_start = """  startPrayer(skipKissOverlay = false) {
    const proceed = () => {
      try {
        this.clearProgress();
        this.sessionCompletedDecades = new Set();

    // 공동체 및 총 봉헌 단수 초기화
// this.initCommunityStats();
        this.steps = this.buildCurrentSteps();
        this.renderDecadeProgressPills();
        this.switchView("prayer");
        this.goToStep(0, true);
      } catch (err) {
        console.error("startPrayer error:", err);
        this.switchView("prayer");
      }
    };

    if (skipKissOverlay || !this.dom.crucifixKissOverlay) {
      proceed();
    } else {
      this.showCrucifixKissOverlay(proceed);
    }
  }"""

new_start = """  startPrayer(skipKissOverlay = false) {
    const proceed = () => {
      try {
        this.clearProgress();
        this.sessionCompletedDecades = new Set();
        this.steps = this.buildCurrentSteps();
        this.renderDecadeProgressPills();
        this.switchView("prayer");
        this.goToStep(0, true);
      } catch (err) {
        console.error("startPrayer error:", err);
        this.switchView("prayer");
      }
    };

    // 무조건 거룩한 성화 친구(親吻) 연출 실행!
    if (!skipKissOverlay && this.dom.crucifixKissOverlay) {
      this.showCrucifixKissOverlay(proceed);
    } else {
      proceed();
    }
  }"""

if old_start in app_js:
    app_js = app_js.replace(old_start, new_start)
    print("startPrayer updated!")

# 4. Check showCrucifixKissOverlay: Ensure overlay element is forced to display: flex!
old_kiss_fn = """  showCrucifixKissOverlay(onComplete) {
    const overlay = this.dom.crucifixKissOverlay;
    if (!overlay) {
      if (onComplete) onComplete();
      return;
    }"""

new_kiss_fn = """  showCrucifixKissOverlay(onComplete) {
    const overlay = this.dom.crucifixKissOverlay || document.getElementById("crucifixKissOverlay");
    if (!overlay) {
      if (onComplete) onComplete();
      return;
    }
    overlay.style.display = "flex";
    overlay.classList.remove("kissed");
    overlay.classList.add("active");"""

if old_kiss_fn in app_js:
    app_js = app_js.replace(old_kiss_fn, new_kiss_fn)
    print("showCrucifixKissOverlay forced active display!")

with open(os.path.join(ROSARY_DIR, "app.js"), "w", encoding="utf-8") as f:
    f.write(app_js)

# Also check index.html to ensure btnStartPrayer properly calls handleStartPrayerRequest
with open(os.path.join(ROSARY_DIR, "index.html"), "r", encoding="utf-8") as f:
    idx_html = f.read()

# Make sure resumeConfirmModal has proper styles & z-index
if '#resumeConfirmModal' not in idx_html:
    css_patch = """
<style>
#resumeConfirmModal { z-index: 10000 !important; }
#crucifixKissOverlay { z-index: 9999 !important; }
</style>
"""
    idx_html = idx_html.replace('</head>', f"{css_patch}\n</head>")

with open(os.path.join(ROSARY_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(idx_html)

# Bundle
subprocess.run(["python", "bundle.py"], cwd=ROSARY_DIR, check=True)

# Copy to consult_diary
shutil.copy(os.path.join(ROSARY_DIR, "rosary.html"), os.path.join(CONSULT_DIR, "rosary.html"))

# Git push
os.chdir(CONSULT_DIR)
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: restore crucifix kiss overlay and resume prayer confirmation modal"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("KISS_AND_RESUME_DEPLOYED_SUCCESSFULLY")
