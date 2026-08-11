Write-Host "=================================================="
Write-Host "  안티그래비티 봇 배포판 만들기 (exe 빌드)"
Write-Host "=================================================="

Write-Host "[1/3] 필요한 패키지 설치 중..."
pip install pyinstaller selenium requests python-dateutil

Write-Host "[2/3] exe 파일 생성 중... (잠시만 기다려주세요)"
pyinstaller --onefile --console --name="중개수첩_오토봇" autobot_launcher.py

Write-Host "[3/3] 배포 폴더 구성 및 압축 중..."
if (-not (Test-Path "배포")) {
    New-Item -ItemType Directory -Path "배포" | Out-Null
}
Copy-Item -Path "dist\중개수첩_오토봇.exe" -Destination "배포\중개수첩_오토봇.exe" -Force
Copy-Item -Path "매뉴얼_안티그래비티봇.txt" -Destination "배포\매뉴얼_안티그래비티봇.txt" -Force

$dateStr = Get-Date -Format "yyMMdd"
$zipName = "Korealtor배포용_$dateStr.zip"

Write-Host "[배포용 압축 파일 생성 중...]"
if (Test-Path $zipName) {
    Remove-Item $zipName -Force
}
Compress-Archive -Path "배포\*" -DestinationPath $zipName -Force

Write-Host "=================================================="
Write-Host "  빌드 및 압축 완료!"
Write-Host "  압축 파일: $zipName"
Write-Host "  배포폴더 위치: $((Get-Location).Path)\배포"
Write-Host "=================================================="
