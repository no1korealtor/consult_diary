import os

path = "d:/부동산업무/antigravity/consult_diary/rosary.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Remove addEventListener on btnStartPrayer which calls handleStart with e.preventDefault()
target_block = """    // 0-5) 인트로 메인 '기도 시작하기' 버튼 클릭 -> 이어할 기록이 있으면 확인 모달, 없으면 시작
    if (this.dom.btnStartPrayer) {
      const handleStart = (e) => {
        if (e && e.cancelable) e.preventDefault();
        this.handleStartPrayerRequest();
      };
      this.dom.btnStartPrayer.addEventListener("click", handleStart);
      this.dom.btnStartPrayer.addEventListener("touchend", handleStart);
    }"""

replacement_block = """    // 0-5) 인트로 메인 '기도 시작하기'는 directStartPrayerAction() 인라인 핸들러에서 100% 보장 처리
    if (this.dom.btnStartPrayer) {
      this.dom.btnStartPrayer.onclick = function(e) {
        if (typeof directStartPrayerAction === 'function') {
          directStartPrayerAction();
        }
      };
    }"""

if target_block in text:
    text = text.replace(target_block, replacement_block)
    print("Replaced handleStart with simple directStartPrayerAction onclick!")
else:
    print("target_block not found exactly, normalizing newlines...")
    t_norm = text.replace("\r\n", "\n")
    tb_norm = target_block.replace("\r\n", "\n")
    rb_norm = replacement_block.replace("\r\n", "\n")
    if tb_norm in t_norm:
        t_norm = t_norm.replace(tb_norm, rb_norm)
        text = t_norm
        print("Replaced handleStart via normalized newlines!")

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

with open("d:/부동산업무/antigravity/rosary-app/index.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Saved files successfully!")
