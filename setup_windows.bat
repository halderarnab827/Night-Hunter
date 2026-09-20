@echo off
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo Installing Python packages...
python -m pip install -r requirement.txt
if errorlevel 1 goto :error

echo Installing frontend packages and building the dashboard...
cd frontend
call npm install
if errorlevel 1 goto :error
call npm run build
if errorlevel 1 goto :error

echo.
echo Setup complete. Double-click start_night_hunter.bat to launch the app.
pause
exit /b 0

:error
echo.
echo Setup failed. Check that Python and Node.js are installed and available in PATH.
pause
exit /b 1
