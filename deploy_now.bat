@echo off
chcp 65001 >nul
cd /d d:\부동산업무\antigravity\consult_diary
git add -A
git commit -m "fix: restore direct button touch and settings handler v136"
git push origin main
echo ====================================
echo DEPLOY COMPLETED SUCCESSFULLY!
echo ====================================
pause
