@echo off
chcp 65001 >nul
cd /d "%~dp0"
python cleanup_modals.py
python force_close_tm.py
python fix_overlay_and_modal.py
git add -A
git commit -m "fix: force close trackerModal overlay completely v142"
git push origin main
echo ====================================
echo SUCCESSFUL_GIT_PUSH_DONE_V142!
echo ====================================
pause
