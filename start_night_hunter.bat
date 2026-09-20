@echo off
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo Starting NIGHT HUNTER on http://127.0.0.1:5000 ...
start "Night Hunter Server" cmd /k "cd /d ""%PROJECT_DIR%"" && python -m waitress --listen=127.0.0.1:5000 api.server:app"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:5000"
