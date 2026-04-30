@echo off
set "PROJ_DIR=%~dp0"
echo Stopping Equity 2 Tier Market Analyzer...

:: Stop Backend if PID file exists
if exist "%PROJ_DIR%logs\backend.pid" (
    for /f %%p in (%PROJ_DIR%logs\backend.pid) do (
        taskkill /F /PID %%p >nul 2>&1 && echo ✓ Backend stopped
    )
    del "%PROJ_DIR%logs\backend.pid"
)

:: Stop Frontend if PID file exists
if exist "%PROJ_DIR%logs\frontend.pid" (
    for /f %%p in (%PROJ_DIR%logs\frontend.pid) do (
        taskkill /F /PID %%p >nul 2>&1 && echo ✓ Frontend stopped
    )
    del "%PROJ_DIR%logs\frontend.pid"
)

:: Kill processes by port (8000 and 3000)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

echo All processes stopped.
