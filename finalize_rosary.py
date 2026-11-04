# -*- coding: utf-8 -*-
with open('rosary.html', 'rb') as f:
    text = f.read().decode('utf-8')

# In HTML:
# Hide meditationBox by default in HTML so Step 0 (Crucifix) does not show Joyful Mystery 1st decade!
text = text.replace('<div id="meditationBox" class="meditation-box">', '<div id="meditationBox" class="meditation-box" style="display: none;">')

# Ensure cardBadge and cardCounter in HTML start cleanly
text = text.replace('<span id="cardBadge" class="card-step-badge">제1단 · 묵상 및 주님의 기도</span>', '<span id="cardBadge" class="card-step-badge">시작 기도 · 십자가 (성호경)</span>')

# In directNextStep and directPrevStep:
# Make them 100% resilient
helpers_new = """
<script>
// [글로벌 직접 제어 핸들러 - 터치 반응 100% 보장]
function directNextStep() {
  try {
    if (window.rosaryApp && typeof window.rosaryApp.nextStep === 'function') {
      window.rosaryApp.nextStep();
      return;
    }
  } catch(e) { console.error('directNextStep error:', e); }
  // 직접 이동 폴백
  try {
    if (window.rosaryApp && typeof window.rosaryApp.goToStep === 'function') {
      window.rosaryApp.goToStep((window.rosaryApp.currentIndex || 0) + 1);
    }
  } catch(e){}
}

function directPrevStep() {
  try {
    if (window.rosaryApp && typeof window.rosaryApp.prevStep === 'function') {
      window.rosaryApp.prevStep();
      return;
    }
  } catch(e) { console.error('directPrevStep error:', e); }
  // 직접 이동 폴백
  try {
    if (window.rosaryApp && typeof window.rosaryApp.goToStep === 'function') {
      window.rosaryApp.goToStep((window.rosaryApp.currentIndex || 0) - 1);
    }
  } catch(e){}
}

function directGoHome() {
  try {
    if (window.rosaryApp && typeof window.rosaryApp.switchView === 'function') {
      window.rosaryApp.switchView('intro');
      return;
    }
  } catch(e) {}
  var pv = document.getElementById('prayerView');
  var yv = document.getElementById('yeondoView');
  var iv = document.getElementById('introView');
  if (pv) pv.style.setProperty('display', 'none', 'important');
  if (yv) yv.style.setProperty('display', 'none', 'important');
  if (iv) {
    iv.style.setProperty('display', 'flex', 'important');
    iv.style.setProperty('opacity', '1', 'important');
    iv.style.setProperty('visibility', 'visible', 'important');
    iv.style.setProperty('z-index', '999', 'important');
  }
}

function directOpenSettings() {
  var m = document.getElementById('settingsModal');
  if (m) {
    m.classList.add('show');
    m.style.setProperty('display', 'flex', 'important');
    m.style.setProperty('opacity', '1', 'important');
    m.style.setProperty('z-index', '99999', 'important');
  }
}

function directOpenTracker() {
  if (window.rosaryApp && typeof window.rosaryApp.renderWeeklyTracker === 'function') {
    try { window.rosaryApp.renderWeeklyTracker(); } catch(e){}
  }
  var m = document.getElementById('trackerModal');
  if (m) {
    m.classList.add('show');
    m.style.setProperty('display', 'flex', 'important');
    m.style.setProperty('opacity', '1', 'important');
    m.style.setProperty('z-index', '99999', 'important');
  }
}
</script>
"""

# Replace helper script block
import re
text = re.sub(r'<script>\s*// \[글로벌 직접 제어.*?</script>', helpers_new.strip(), text, flags=re.DOTALL)

with open('rosary.html', 'wb') as f:
    f.write(text.encode('utf-8'))

print("Completed finalize_rosary.py")
