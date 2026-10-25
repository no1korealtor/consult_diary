import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's find any modal or overlay that might be covering the screen
# Especially trackerModal or crucifixKissOverlay or resumeModal
# Check if trackerModal has "show" or is active by default in HTML
print("trackerModal classes:", "id=\"trackerModal\"" in text)

# In directOpenSettings, let's close all other modals first, and make sure settingsModal is visible and has highest z-index
enhanced_script = """
<script>
// [원터치 언어 전환]
function toggleGlobalLanguage() {
  try {
    var cur = (window.rosaryApp && window.rosaryApp.settings) ? (window.rosaryApp.settings.lang || 'ko') : (localStorage.getItem('rosary_prayer_lang') || 'ko');
    var next = (cur === 'en') ? 'ko' : 'en';
    
    if (window.rosaryApp && typeof window.rosaryApp.setLanguage === 'function') {
      window.rosaryApp.setLanguage(next);
    } else {
      localStorage.setItem('rosary_prayer_lang', next);
    }
    
    var btn = document.getElementById('btnHeaderLangToggle');
    if (btn) btn.textContent = (next === 'en') ? '🌐 한' : '🌐 EN';
    
    var title = document.getElementById('introHeroTitle');
    var startBtnTxt = document.getElementById('btnStartPrayerText');
    if (next === 'en') {
      if (title) title.textContent = 'The Holy Rosary';
      if (startBtnTxt) startBtnTxt.textContent = 'Start Holy Rosary';
    } else {
      if (title) title.textContent = '거룩한 묵주기도';
      if (startBtnTxt) startBtnTxt.textContent = '묵주기도 시작하기';
    }
  } catch(e) {
    console.error('toggleGlobalLanguage error:', e);
  }
}

function closeAllModalsDirect() {
  document.querySelectorAll('.modal-backdrop').forEach(function(m) {
    m.classList.remove('show');
    m.style.display = 'none';
  });
}

function openSettingsDirect() {
  try {
    closeAllModalsDirect();
    var m = document.getElementById('settingsModal');
    if (m) {
      m.classList.add('show');
      m.style.setProperty('display', 'flex', 'important');
      m.style.setProperty('opacity', '1', 'important');
      m.style.setProperty('pointer-events', 'auto', 'important');
      m.style.setProperty('z-index', '99999', 'important');
      var s = m.querySelector('.bottom-sheet');
      if (s) {
        s.style.setProperty('transform', 'translateY(0)', 'important');
      }
    }
  } catch(e) {
    console.error('openSettingsDirect error:', e);
  }
}

function closeSettingsDirect() {
  var m = document.getElementById('settingsModal');
  if (m) {
    m.classList.remove('show');
    m.style.setProperty('display', 'none', 'important');
  }
}

function directStartPrayerAction() {
  try {
    closeAllModalsDirect();
    if (window.rosaryApp && typeof window.rosaryApp.handleStartPrayerRequest === 'function') {
      window.rosaryApp.handleStartPrayerRequest();
      return;
    }
  } catch(err) {
    console.warn('rosaryApp handler warning:', err);
  }

  try {
    var iv = document.getElementById('introView');
    var pv = document.getElementById('prayerView');
    var yv = document.getElementById('yeondoView');
    if (iv) iv.style.setProperty('display', 'none', 'important');
    if (yv) yv.style.setProperty('display', 'none', 'important');
    if (pv) pv.style.setProperty('display', 'flex', 'important');

    if (window.rosaryApp) {
      if (typeof window.rosaryApp.startPrayer === 'function') {
        window.rosaryApp.startPrayer(true);
      } else if (typeof window.rosaryApp.goToStep === 'function') {
        window.rosaryApp.goToStep(0, true);
      }
    }
  } catch(e) {
    console.error('directStartPrayerAction fallback error:', e);
  }
}
</script>
"""

# Replace script at the end
idx_s = text.find("// [전역 원터치 언어 전환 함수]")
if idx_s != -1:
    s_tag_start = text.rfind("<script", 0, idx_s)
    text = text[:s_tag_start] + enhanced_script + "\n</body>\n</html>"
    print("Replaced tail script with enhanced_script!")

# Also ensure closeTrackerBtn onclick is set to direct close
text = text.replace('id="closeTrackerBtn" class="tracker-close-btn" aria-label="닫기">✕</button>', 'id="closeTrackerBtn" class="tracker-close-btn" onclick="var m=document.getElementById(\'trackerModal\');if(m){m.classList.remove(\'show\');m.style.display=\'none\';}" aria-label="닫기">✕</button>')

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Saved files!")
