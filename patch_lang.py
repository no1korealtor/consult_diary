import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "rb") as f:
    raw = f.read()

# Replace toggleGlobalLanguage
old_str = """function toggleGlobalLanguage() {
  try {
    if (!window.rosaryApp) return;
    const cur = window.rosaryApp.settings.lang || 'ko';
    const next = (cur === 'en') ? 'ko' : 'en';
    window.rosaryApp.setLanguage(next);
    
    // 버튼 텍스트 변경
    const btn = document.getElementById('btnHeaderLangToggle');
    if (btn) {
      btn.textContent = (next === 'en') ? '🌐 한' : '🌐 EN';
    }
  } catch(e) {
    console.error('toggleGlobalLanguage error:', e);
  }
}""".encode("utf-8")

new_str = """function toggleGlobalLanguage() {
  try {
    var cur = (window.rosaryApp && window.rosaryApp.settings) ? (window.rosaryApp.settings.lang || 'ko') : (localStorage.getItem('rosary_prayer_lang') || 'ko');
    var next = (cur === 'en') ? 'ko' : 'en';
    
    if (window.rosaryApp && typeof window.rosaryApp.setLanguage === 'function') {
      window.rosaryApp.setLanguage(next);
    } else {
      localStorage.setItem('rosary_prayer_lang', next);
    }
    
    // 버튼 텍스트 즉시 변경
    var btn = document.getElementById('btnHeaderLangToggle');
    if (btn) {
      btn.textContent = (next === 'en') ? '🌐 한' : '🌐 EN';
    }
    
    // 화면 내 주요 텍스트 즉시 반영
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
}""".encode("utf-8")

if old_str in raw:
    raw = raw.replace(old_str, new_str)
    print("Replaced toggleGlobalLanguage successfully!")
else:
    print("old_str not found in raw bytes, normalizing newlines...")
    raw_text = raw.decode("utf-8")
    old_text = old_str.decode("utf-8").replace("\r\n", "\n")
    raw_text_norm = raw_text.replace("\r\n", "\n")
    if old_text in raw_text_norm:
        raw_text_norm = raw_text_norm.replace(old_text, new_str.decode("utf-8").replace("\r\n", "\n"))
        raw = raw_text_norm.encode("utf-8")
        print("Replaced toggleGlobalLanguage via normalized newlines!")
    else:
        print("Failed to find old_text even with normalization")

with open(path, "wb") as f:
    f.write(raw)

# Also copy to rosary-app/index.html
with open("d:/부동산업무/antigravity/rosary-app/index.html", "wb") as f:
    f.write(raw)

print("Saved files successfully!")
