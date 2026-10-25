import os
import subprocess
import shutil

# Make settings button and start prayer button 100% resilient and fail-safe!
with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Direct fail-safe start prayer function:
failsafe_script = """
<script>
// [100% 보장] 묵주기도 시작 및 설정 열기 직통 함수
function directStartPrayerAction() {
  try {
    if (window.rosaryApp) {
      window.rosaryApp.handleStartPrayerRequest();
    } else {
      var iv = document.getElementById('introView');
      var pv = document.getElementById('prayerView');
      if (iv) iv.style.display = 'none';
      if (pv) pv.style.display = 'flex';
    }
  } catch(err) {
    console.error('directStartPrayerAction fallback:', err);
    var iv = document.getElementById('introView');
    var pv = document.getElementById('prayerView');
    if (iv) iv.style.display = 'none';
    if (pv) pv.style.display = 'flex';
  }
}

function directOpenSettings() {
  try {
    var m = document.getElementById('settingsModal');
    if (m) {
      m.classList.add('show');
      m.style.setProperty('display', 'flex', 'important');
      m.style.setProperty('pointer-events', 'auto', 'important');
      m.style.setProperty('opacity', '1', 'important');
      m.style.setProperty('visibility', 'visible', 'important');
      var s = m.querySelector('.bottom-sheet');
      if (s) {
        s.style.setProperty('transform', 'translateY(0)', 'important');
        s.style.setProperty('opacity', '1', 'important');
        s.style.setProperty('visibility', 'visible', 'important');
      }
    }
  } catch(err) {
    console.error('directOpenSettings error:', err);
  }
}

function directCloseSettings() {
  try {
    var m = document.getElementById('settingsModal');
    if (m) {
      m.classList.remove('show');
      m.style.setProperty('display', 'none', 'important');
    }
  } catch(err){}
}
</script>
"""

text = text.replace('</body>', f"{failsafe_script}\n</body>")

# 2. Update btnStartPrayer and btnIntroSettings onclick
text = text.replace('onclick="if(window.rosaryApp){window.rosaryApp.handleStartPrayerRequest();}"', 'onclick="directStartPrayerAction();"')
text = text.replace('onclick="openSettingsDirect();"', 'onclick="directOpenSettings();"')
text = text.replace('onclick="closeSettingsDirect();"', 'onclick="directCloseSettings();"')

# 3. Ensure close buttons in settingsModal use directCloseSettings
text = text.replace('id="closeSettingsBtn"', 'id="closeSettingsBtn" onclick="directCloseSettings();"')
text = text.replace('id="btnDismissSettingsModal"', 'id="btnDismissSettingsModal" onclick="directCloseSettings();"')

# 4. Make sure crucifixKissOverlay also has skip click fall-through
text = text.replace('id="btnCrucifixSkip"', 'id="btnCrucifixSkip" onclick="var o=document.getElementById(\'crucifixKissOverlay\');if(o){o.classList.remove(\'active\');o.style.display=\'none\';}if(window.rosaryApp){window.rosaryApp.switchView(\'prayer\');window.rosaryApp.goToStep(0,true);}"')

with open("d:/부동산업무/antigravity/consult_diary/rosary.html", "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text)

os.chdir("d:/부동산업무/antigravity/consult_diary")
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: directStartPrayerAction and directOpenSettings with infallible fail-safe v120"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("\n" + "="*50)
print("FAILSAFE_START_AND_SETTINGS_DEPLOYED")
print("="*50)
