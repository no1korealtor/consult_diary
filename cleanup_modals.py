import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Look for all modal-backdrop divs and make sure NONE of them have 'show' class or inline display:flex by default
import re
modals = re.findall(r'<div[^>]*class="[^"]*modal-backdrop[^"]*"[^>]*>', text)
print("Found modals:", modals)

# If any modal has 'show', remove it
text = re.sub(r'(class="[^"]*modal-backdrop[^"]*)\s+show([^"]*")', r'\1\2', text)

# 2. Make sure trackerModal has display: none !important by default inline to prevent any accidental display
text = text.replace('id="trackerModal" class="modal-backdrop"', 'id="trackerModal" class="modal-backdrop" style="display: none;"')
text = text.replace('id="settingsModal" class="modal-backdrop"', 'id="settingsModal" class="modal-backdrop" style="display: none;"')

# 3. Add an auto-cleanup script at the very top of <body> to ensure all modals are closed upon page load
startup_script = """
<script>
// [시작 시 화면 가림 방지] 모든 모달 초기화
(function() {
  function hideAllModalsOnStart() {
    document.querySelectorAll('.modal-backdrop').forEach(function(m) {
      m.classList.remove('show');
      m.style.display = 'none';
    });
    var ck = document.getElementById('crucifixKissOverlay');
    if (ck) {
      ck.classList.remove('show');
      ck.style.display = 'none';
    }
  }
  hideAllModalsOnStart();
  document.addEventListener('DOMContentLoaded', hideAllModalsOnStart);
  window.addEventListener('load', hideAllModalsOnStart);
})();
</script>
"""

if '<div id="app">' in text:
    text = text.replace('<div id="app">', startup_script + '\n  <div id="app">', 1)
    print("Injected startup_script before #app!")

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Saved files successfully!")
