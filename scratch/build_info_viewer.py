import os
import shutil
import subprocess
import zipfile
from datetime import datetime

print("==================================================")
print("  부동산 정보 조회기 standalone 배포판 만들기 (exe 빌드)")
print("==================================================")

# 1. Install packages
print("[1/3] 필요한 패키지 설치 확인 중...")
subprocess.run(["pip", "install", "pyinstaller", "requests", "python-dateutil", "reportlab"], check=True)

# 2. PyInstaller
print("[2/3] exe 파일 생성 중... (잠시만 기다려주세요)")
subprocess.run(["python", "-m", "PyInstaller", "--onefile", "--console", "--name=부동산정보_조회기", "info_viewer_launcher.py"], check=True)

# 3. Create deploy folder
print("[3/3] 배포 폴더 구성 및 압축 중...")
deploy_dir = "배포_부동산정보_조회기"
if os.path.exists(deploy_dir):
    shutil.rmtree(deploy_dir)
os.makedirs(deploy_dir)

# Copy files
shutil.copy2(os.path.join("dist", "부동산정보_조회기.exe"), os.path.join(deploy_dir, "부동산정보_조회기.exe"))
shutil.copy2("매뉴얼_부동산정보_조회기.txt", os.path.join(deploy_dir, "매뉴얼_부동산정보_조회기.txt"))

# Zip
date_str = datetime.now().strftime("%y%m%d_%H%M")
zip_name = f"부동산정보_조회기_배포용_{date_str}.zip"
print(f"[배포용 압축 파일 생성 중...] -> {zip_name}")

if os.path.exists(zip_name):
    os.remove(zip_name)

with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(deploy_dir):
        for file in files:
            file_path = os.path.join(root, file)
            # Add file to zip with relative path (inside the folder structure)
            zipf.write(file_path, os.path.join("배포_부동산정보_조회기", file))

print("==================================================")
print("  빌드 및 압축 완료!")
print(f"  압축 파일: {zip_name}")
print(f"  배포폴더 위치: {os.path.abspath(deploy_dir)}")
print("==================================================")
