@echo off
setlocal
cd /d "%~dp0"

echo ======================================================
echo  Rosary App Safe Deployment Process
echo ======================================================

echo [1/3] Verifying code integrity and button actions...
python verify_deploy.py
if errorlevel 1 (
    echo.
    echo [ERROR] Verification failed! Deployment aborted.
    echo.
    pause
    exit /b 1
)

echo.
echo [2/3] Verification passed! Adding files to git...
git add rosary.html verify_deploy.py push.bat
git commit -m "feat: add sacred crucifix art to prayer card and deploy verification pipeline"

echo.
echo [3/3] Pushing to GitHub origin main...
git push origin main
if errorlevel 1 (
    echo.
    echo [ERROR] Git push failed.
    pause
    exit /b 1
)

echo.
echo ======================================================
echo  Deployment completed safely and successfully!
echo ======================================================
