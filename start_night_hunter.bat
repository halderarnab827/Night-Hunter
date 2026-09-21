@echo off
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo ========================================================
echo        NIGHT HUNTER - DEFENSIVE SECURITY PLATFORM
echo ========================================================
echo Connecting directly to Night Hunter Live Cloud Server...
echo Any patches or updates are automatically live!
echo.
start "Night Hunter Server" cmd /k "cd /d ""%PROJECT_DIR%"" && python -m waitress --listen=127.0.0.1:5000 api.server:app"
timeout /t 2 /nobreak >nul
start "" "https://night-hunter-f2w4.onrender.com/app"
