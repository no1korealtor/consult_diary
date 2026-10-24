import subprocess
import os
import sys

# 현재 consult_diary 폴더에서 상대경로로 상위 폴더 찾기
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
ROSARY_APP_DIR = os.path.join(PARENT_DIR, "rosary-app")

print(f"Current Dir: {CURRENT_DIR}")
print(f"Parent Dir: {PARENT_DIR}")

# 1. Update source
print("\n[1/5] Update source HTML...")
update_src_script = os.path.join(PARENT_DIR, "update_source.py")
subprocess.run([sys.executable, update_src_script], check=True)

# 2. Make icons
print("\n[2/5] Make Gold Icons...")
make_icons_script = os.path.join(PARENT_DIR, "make_icons_sync.py")
subprocess.run([sys.executable, make_icons_script], check=True)

# 3. Bundle
print("\n[3/5] Bundle rosary.html...")
bundle_script = os.path.join(ROSARY_APP_DIR, "bundle.py")
subprocess.run([sys.executable, bundle_script], cwd=ROSARY_APP_DIR, check=True)

# 4. Copy to consult_diary
print("\n[4/5] Copying rosary.html to consult_diary...")
src_html = os.path.join(ROSARY_APP_DIR, "rosary.html")
dst_html = os.path.join(CURRENT_DIR, "rosary.html")
with open(src_html, "rb") as sf, open(dst_html, "wb") as df:
    df.write(sf.read())

# 5. Git commit & push
print("\n[5/5] Deploying to GitHub...")
os.chdir(CURRENT_DIR)
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix(pwa): force update gold icons and dedicated rosary-manifest v50"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("\n" + "="*50)
print("SUCCESS! ALL DEPLOYMENT COMPLETE!")
print("="*50)
input("\nPress Enter to exit...")
