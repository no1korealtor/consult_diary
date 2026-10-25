@echo off
chcp 65001 >nul
cd /d "%~dp0"
python add_sacred_art.py
python bulletproof_start.py
git add -A
git commit -m "fix: bulletproof instant transition to prayerView on start button v144"
git push origin main
echo ====================================
echo SUCCESSFUL_GIT_PUSH_DONE_V144!
echo ====================================
pause
