import subprocess
import os
import sys

print("1. Running fix_pwa_scope...")
subprocess.run([sys.executable, "fix_pwa_scope.py"], check=True)

print("2. Git add...")
subprocess.run(["git", "add", "-A"], check=True)

print("3. Git commit...")
subprocess.run(["git", "commit", "-m", "fix: separate rosary pwa from consult diary webapk"], check=False)

print("4. Git push...")
subprocess.run(["git", "push", "origin", "main"], check=True)

print("\n" + "="*50)
print("SUCCESS! PWA SEPARATED & DEPLOYED!")
print("="*50)
