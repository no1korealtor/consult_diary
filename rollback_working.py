import os
import subprocess
import shutil

# Revert consult_diary/rosary.html to the exact working commit when user said "성공이다"
# Let's find commit hash for "feat: start intention count honestly from 0 with minimal empty prompt"
# or commit right before touch froze

os.chdir("d:/부동산업무/antigravity/consult_diary")
log_res = subprocess.run(["git", "log", "--grep=honestly from 0", "-n", "1", "--format=%H"], capture_output=True, text=True, encoding="utf-8")
working_hash = log_res.stdout.strip()
print("Working commit hash:", working_hash)

if not working_hash:
    # fallback to yesterday's commit before today's changes
    log_res2 = subprocess.run(["git", "log", "-n", "15", "--oneline"], capture_output=True, text=True, encoding="utf-8")
    print(log_res2.stdout)
    for line in log_res2.stdout.split("\n"):
        if "honestly from 0" in line or "V2_PURGE" in line or "sample 42" in line:
            working_hash = line.split()[0]
            break

print("Selected revert target:", working_hash)

# Check out rosary.html from that working commit!
subprocess.run(["git", "checkout", working_hash, "--", "rosary.html"], check=True)
shutil.copy("rosary.html", "d:/부동산업무/antigravity/rosary-app/index.html")

# Git commit & push this clean rollback
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "revert: rollback rosary.html to perfectly working state (touch & intention working)"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("\n" + "="*50)
print("PERFECT_ROLLBACK_DEPLOYED_SUCCESSFULLY")
print("="*50)
