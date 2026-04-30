@echo off
REM ============================================================
REM  Voice Authenticator — Windows Startup Script
REM ============================================================

set PROJ_DIR=%~dp0
set BACKEND_DIR=%PROJ_DIR%backend
set FRONTEND_DIR=%PROJ_DIR%frontend

echo.
echo ========================================================
echo   Voice Authentication System
echo   World-Class Voice Authentication System
echo ========================================================
echo.



REM Create venv
IF NOT EXIST "%BACKEND_DIR%\venv" (
    echo Creating Python virtual environment...
    python -m venv "%BACKEND_DIR%\venv"
)


REM Start backend
echo Starting backend...
cd /d "%BACKEND_DIR%"
call venv\Scripts\activate.bat
start "Voice Authenticator - Backend" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait for backend
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting frontend...
cd /d "%FRONTEND_DIR%"
start "Voice Authenticator - Frontend" cmd /k "npm run dev"

echo.
echo ========================================================
echo   APPLICATION STARTED
echo ========================================================
echo.
echo   Frontend:  http://localhost:3000
echo   API:       http://localhost:8000
echo   API Docs:  http://localhost:8000/api/docs
echo.
echo   Login: admin / admin@123   (ADMIN)
echo          analyst / analyst123 (ANALYST)
echo.
pause
