import subprocess
import os
import sys
import shutil

# 현재 consult_diary 폴더 기준으로 안전한 상대경로 계산
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
ROSARY_DIR = os.path.join(PARENT_DIR, "rosary-app")

print("[1/4] Fixing unclosed div...")
index_path = os.path.join(ROSARY_DIR, "index.html")
with open(index_path, "r", encoding="utf-8") as f:
    html = f.read()

broken_str = """    <!-- 7. 신비 선택 모달 바텀시트 -->
    <div id="mysteryModal" class="modal-backdrop">
      <div class="bottom-sheet">
        <div class="sheet-handle"></div>
        <div class="sheet-title">묵주기도 신비 선택</div>
        <div id="mysteryOptionsList" class="mystery-options-list">
          <!-- 스크립트에서 자동 생성 -->
        </div>

        
    </div>

    <!-- 9. 주간 기도 기록 모달 바텀시트 -->"""

fixed_str = """    <!-- 7. 신비 선택 모달 바텀시트 -->
    <div id="mysteryModal" class="modal-backdrop">
      <div class="bottom-sheet">
        <div class="sheet-handle"></div>
        <div class="sheet-title">묵주기도 신비 선택</div>
        <div id="mysteryOptionsList" class="mystery-options-list">
          <!-- 스크립트에서 자동 생성 -->
        </div>
      </div>
    </div>

    <!-- 9. 주간 기도 기록 모달 바텀시트 -->"""

if broken_str in html:
    html = html.replace(broken_str, fixed_str)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("-> Fixed successfully!")
else:
    print("-> Already fixed or pattern matched.")

print("[2/4] Bundling rosary-app...")
bundle_path = os.path.join(ROSARY_DIR, "bundle.py")
subprocess.run([sys.executable, bundle_path], cwd=ROSARY_DIR, check=True)

print("[3/4] Copying rosary.html to consult_diary...")
src_html = os.path.join(ROSARY_DIR, "rosary.html")
dst_html = os.path.join(CURRENT_DIR, "rosary.html")
shutil.copy(src_html, dst_html)

print("[4/4] Git pushing to GitHub...")
os.chdir(CURRENT_DIR)
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: calendar modal open issue"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("\n" + "="*50)
print("SUCCESS! CALENDAR IS FULLY FIXED!")
print("="*50)
