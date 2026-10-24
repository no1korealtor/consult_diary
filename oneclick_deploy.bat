@echo off
setlocal

echo [1/4] Replace HTML...
python "d:\부동산업무\antigravity\replace_html.py"

echo [2/4] Make Icons...
python "d:\부동산업무\antigravity\make_icons_sync.py"

echo [3/4] Bundle...
python "d:\부동산업무\antigravity\rosary-app\bundle.py"

echo [4/4] Git Deploy...
cd /d "d:\부동산업무\antigravity\consult_diary"
git add -A
git commit -m "feat: update pwa icons v47"
git push origin main

echo.
echo ========================================
echo SUCCESS! DEPLOYMENT FINISHED!
echo ========================================
echo Press any key to close this window.
pause
