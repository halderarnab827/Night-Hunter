@echo off
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo ========================================================
echo        NIGHT HUNTER - DEFENSIVE SECURITY PLATFORM
echo ========================================================
echo Starting your local Night Hunter dashboard...
echo The app will open at http://127.0.0.1:5000
echo.
start "Night Hunter Server" cmd /k "cd /d ""%PROJECT_DIR%"" && python -m waitress --listen=127.0.0.1:5000 api.server:app"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:5000/app"
