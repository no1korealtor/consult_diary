@echo off
chcp 65001 >nul
cd /d "%~dp0"
python restore_gotostep.py
python kill_cache.py
git add -A
git commit -m "fix: restore missing goToStep method in RosaryApp v146"
git push origin main
echo ====================================
echo SUCCESSFUL_GIT_PUSH_DONE_V146!
echo ====================================
pause
