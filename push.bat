@echo off
chcp 65001 >nul
cd /d "%~dp0"
python fix_overlay_and_modal.py
git add -A
git commit -m "fix: dismiss trackerModal overlay and connect direct handlers v140"
git push origin main
echo ====================================
echo SUCCESSFUL_GIT_PUSH_DONE_V140!
echo ====================================
pause
