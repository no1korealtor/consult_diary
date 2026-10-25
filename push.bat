@echo off
chcp 65001 >nul
cd /d "%~dp0"
python fix_touch_event.py
python kill_cache.py
git add -A
git commit -m "fix: remove preventDefault on btnStartPrayer and bind direct start action v145"
git push origin main
echo ====================================
echo SUCCESSFUL_GIT_PUSH_DONE_V145!
echo ====================================
pause
