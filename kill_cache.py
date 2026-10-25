import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Unregister all service workers and wipe all caches completely!
sw_killer = """
  <script>
    // [강력 캐시 완전 삭제 및 서비스워커 즉각 파기]
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.getRegistrations().then(function(registrations) {
        for (let registration of registrations) {
          registration.unregister();
        }
      });
    }
    if ('caches' in window) {
      caches.keys().then(function(names) {
        for (let name of names) caches.delete(name);
      });
    }
  </script>
"""

# Replace existing serviceWorker block
idx_sw = text.find("// 서비스 워커 등록 및 구버전 캐시 자동 정리")
if idx_sw != -1:
    s_start = text.rfind("<script", 0, idx_sw)
    s_end = text.find("</script>", idx_sw) + 9
    text = text[:s_start] + sw_killer + text[s_end:]
    print("Replaced service worker with killer script!")

# 2. Add an explicit close button handler and click outside close to modal-backdrop
modal_click_close = """
<script>
// 모달 배경 클릭 시 100% 즉시 닫기
document.addEventListener('click', function(e) {
  if (e.target.classList.contains('modal-backdrop')) {
    e.target.classList.remove('show');
    e.target.style.setProperty('display', 'none', 'important');
  }
});
</script>
"""

text = text.replace("</body>", modal_click_close + "\n</body>")

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated cache-killer and modal-closer!")
