@echo off
chcp 65001 >nul
cd /d "%~dp0"
python restore_settings_modal.py
python patch_lang.py
python fix_start_btn.py
git add -A
git commit -m "fix: restore settingsModal, directStartPrayerAction, lang toggle v139"
git push origin main
echo ====================================
echo SUCCESSFUL_GIT_PUSH_DONE_V139!
echo ====================================
pause
