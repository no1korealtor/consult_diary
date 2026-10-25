import os
import subprocess
import shutil

ROSARY_DIR = "d:/부동산업무/antigravity/rosary-app"
CONSULT_DIR = "d:/부동산업무/antigravity/consult_diary"

with open(os.path.join(ROSARY_DIR, "index.html"), "r", encoding="utf-8") as f:
    html = f.read()

# Force clear sample 42 in localStorage on version bump to v70
clear_sample_code = """
<script>
// [버전 업데이트] 기존 예시 42명 샘플 지향 자동 정리 -> 정직한 초기 상태(0명/대기상태)로 전환
try {
  const cur = localStorage.getItem('rosary_community_intention_v1');
  if (cur && cur.includes('int_sample_01')) {
    localStorage.removeItem('rosary_community_intention_v1');
    localStorage.removeItem('rosary_joined_intention_id_v1');
  }
} catch(e){}
</script>
"""

if "int_sample_01" not in html:
    html = html.replace("<body>", f"<body>\n{clear_sample_code}\n", 1)

with open(os.path.join(ROSARY_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

# Bundle
subprocess.run(["python", "bundle.py"], cwd=ROSARY_DIR, check=True)

# Copy to consult_diary
shutil.copy(os.path.join(ROSARY_DIR, "rosary.html"), os.path.join(CONSULT_DIR, "rosary.html"))

# Git push
os.chdir(CONSULT_DIR)
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "fix: clear sample 42 from localStorage on client devices"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("SAMPLE_CLEARED_AND_DEPLOYED_SUCCESSFULLY")
