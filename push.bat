@echo off
chcp 65001 >nul
cd /d "%~dp0"
copy /y rosary.html ..\rosary-app\index.html
git add -A
git commit -m "fix: direct buttons and settings handler v136"
git push origin main
echo ====================================
echo SUCCESSFUL_GIT_PUSH_DONE!
echo ====================================
pause
