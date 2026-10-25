import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Make sure directStartPrayerAction handles startPrayer immediately without any blocking or unhandled exceptions
direct_start_script = """
<script>
// [초강력 즉시 실행] 묵주기도 시작 및 뷰 전환 직통 함수
function directStartPrayerAction() {
  try {
    // 1. 만약 앱 인스턴스가 존재하면 공식 핸들러 실행
    if (window.rosaryApp && typeof window.rosaryApp.handleStartPrayerRequest === 'function') {
      window.rosaryApp.handleStartPrayerRequest();
      return;
    }
  } catch(err) {
    console.warn('rosaryApp handler warning:', err);
  }

  // 2. 만약 앱 인스턴스에서 에러가 나거나 로딩 중이면 즉시 기도 화면(prayerView)으로 직통 진입
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
    var iv = document.getElementById('introView');
    var pv = document.getElementById('prayerView');
    if (iv) iv.style.display = 'none';
    if (pv) pv.style.display = 'flex';
  }
}
</script>
"""

if "function directStartPrayerAction()" in text:
    idx1 = text.find("function directStartPrayerAction()")
    # find enclosing script tag
    s_start = text.rfind("<script", 0, idx1)
    s_end = text.find("</script>", idx1) + 9
    text = text[:s_start] + direct_start_script + text[s_end:]
    print("Updated directStartPrayerAction with foolproof fallback!")

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated directStartPrayerAction script in files!")
