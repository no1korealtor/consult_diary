import os
import subprocess
import shutil

ROSARY_DIR = "d:/부동산업무/antigravity/rosary-app"
CONSULT_DIR = "d:/부동산업무/antigravity/consult_diary"

with open(os.path.join(ROSARY_DIR, "index.html"), "r", encoding="utf-8") as f:
    text = f.read()

# Force hardcode empty prompt and remove any 42
text = text.replace('42', '0')
text = text.replace('수술을 앞둔 어머니(데레사)의 평안과 쾌유를 위해 기도 부탁드립니다.', '')

# In JS logic, make STORAGE_KEY version 2 so it completely ignores old sample
text = text.replace("STORAGE_KEY = 'rosary_community_intention_v1'", "STORAGE_KEY = 'rosary_community_intention_v2'")
text = text.replace("JOINED_KEY = 'rosary_joined_intention_id_v1'", "JOINED_KEY = 'rosary_joined_intention_id_v2'")

# Remove defaultIntention object completely, return null if no user intention
old_fn_start = 'function getStoredIntention() {'
new_fn = """function getStoredIntention() {
    try {
      const raw = localStorage.getItem('rosary_community_intention_v2');
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      return (parsed && parsed.active && parsed.text) ? parsed : null;
    } catch(e) {
      return null;
    }
  }"""

if old_fn_start in text:
    end_fn = text.find('function saveStoredIntention', text.find(old_fn_start))
    text = text[:text.find(old_fn_start)] + new_fn + "\n\n  " + text[end_fn:]

with open(os.path.join(ROSARY_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(text)

# Bundle
subprocess.run(["python", "bundle.py"], cwd=ROSARY_DIR, check=True)

# Copy to consult_diary
shutil.copy(os.path.join(ROSARY_DIR, "rosary.html"), os.path.join(CONSULT_DIR, "rosary.html"))

# Git push
os.chdir(CONSULT_DIR)
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: bump intention storage to v2 and purge sample 42 completely"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("V2_PURGE_DEPLOYED_SUCCESSFULLY")
