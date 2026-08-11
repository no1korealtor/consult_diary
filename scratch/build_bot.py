import os
import shutil
import subprocess
import zipfile
from datetime import datetime

print("==================================================")
print("  안티그래비티 봇 배포판 만들기 (exe 빌드)")
print("==================================================")

# 1. Install packages
print("[1/3] 필요한 패키지 설치 중...")
subprocess.run(["pip", "install", "pyinstaller", "selenium", "requests", "python-dateutil", "reportlab"], check=True)

# 2. PyInstaller
print("[2/3] exe 파일 생성 중... (잠시만 기다려주세요)")
subprocess.run(["python", "-m", "PyInstaller", "--onefile", "--console", "--name=중개수첩_오토봇", "--collect-all=selenium", "--clean", "autobot_launcher.py"], check=True)

# 3. Create deploy folder
print("[3/3] 배포 폴더 구성 및 압축 중...")
deploy_dir = "배포"
if not os.path.exists(deploy_dir):
    os.makedirs(deploy_dir)

# Copy files
shutil.copy2(os.path.join("dist", "중개수첩_오토봇.exe"), os.path.join(deploy_dir, "중개수첩_오토봇.exe"))
shutil.copy2("매뉴얼_안티그래비티봇.txt", os.path.join(deploy_dir, "매뉴얼_안티그래비티봇.txt"))

# Zip
date_str = datetime.now().strftime("%y%m%d_%H%M")
zip_name = f"Korealtor배포용_{date_str}.zip"
print(f"[배포용 압축 파일 생성 중...] -> {zip_name}")

if os.path.exists(zip_name):
    os.remove(zip_name)

with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(deploy_dir):
        for file in files:
            file_path = os.path.join(root, file)
            # Add file to zip with relative path (inside the '배포' folder structure)
            zipf.write(file_path, os.path.join("배포", file))

print("==================================================")
print("  빌드 및 압축 완료!")
print(f"  압축 파일: {zip_name}")
print(f"  배포폴더 위치: {os.path.abspath(deploy_dir)}")
print("==================================================")
