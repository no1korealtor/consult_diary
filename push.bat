@echo off
chcp 65001 >nul
cd /d "%~dp0"
python kill_cache.py
python force_close_tm.py
git add -A
git commit -m "fix: kill PWA serviceWorker cache and force close overlays v143"
git push origin main
echo ====================================
echo SUCCESSFUL_GIT_PUSH_DONE_V143!
echo ====================================
pause
