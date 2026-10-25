import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Check what happens when btnStartPrayer is clicked:
# In rosary.html:
# <button type="button" id="btnStartPrayer" class="intro-main-start-btn" onclick="directStartPrayerAction();">
# Let's inspect directStartPrayerAction in rosary.html:
print("directStartPrayerAction exists:", "directStartPrayerAction()" in text)

# Now check: In RosaryApp.bindEvents():
# this.dom.btnStartPrayer.addEventListener("click", handleStart);
# Let's ensure startPrayer directly shows the prayerView and never gets blocked!
# Let's make startPrayer bypass kiss overlay if user clicks startPrayer directly
bulletproof_start = """
function directStartPrayerAction() {
  try {
    closeAllModalsDirect();
    
    // 1. 인트로 뷰 즉시 숨기고 기도 뷰 즉시 노출
    var iv = document.getElementById('introView');
    var pv = document.getElementById('prayerView');
    var yv = document.getElementById('yeondoView');
    if (iv) iv.style.setProperty('display', 'none', 'important');
    if (yv) yv.style.setProperty('display', 'none', 'important');
    if (pv) pv.style.setProperty('display', 'flex', 'important');

    // 2. 앱 인스턴스에 기도 시작 알림
    if (window.rosaryApp) {
      window.rosaryApp.currentView = 'prayer';
      if (typeof window.rosaryApp.clearProgress === 'function') {
        window.rosaryApp.clearProgress();
      }
      if (typeof window.rosaryApp.buildCurrentSteps === 'function') {
        window.rosaryApp.steps = window.rosaryApp.buildCurrentSteps();
      }
      if (typeof window.rosaryApp.renderDecadeProgressPills === 'function') {
        window.rosaryApp.renderDecadeProgressPills();
      }
      if (typeof window.rosaryApp.goToStep === 'function') {
        window.rosaryApp.goToStep(0, true);
      }
    }
  } catch(e) {
    console.error('directStartPrayerAction error:', e);
    var iv = document.getElementById('introView');
    var pv = document.getElementById('prayerView');
    if (iv) iv.style.display = 'none';
    if (pv) pv.style.display = 'flex';
  }
}
"""

idx_f = text.find("function directStartPrayerAction()")
if idx_f != -1:
    idx_end = text.find("</script>", idx_f)
    text = text[:idx_f] + bulletproof_start.strip() + "\n" + text[idx_end:]
    print("Replaced directStartPrayerAction with bulletproof instant prayer view transition!")

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Saved files!")
