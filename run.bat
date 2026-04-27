@echo off
title TalentScout AI — Launcher
color 0A
cls

echo.
echo  ==========================================
echo   TalentScout AI - Starting Servers
echo  ==========================================
echo.

REM ── Kill any existing instances ─────────────────────────
echo  Cleaning up old processes...
taskkill /F /IM uvicorn.exe >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173"') do taskkill /F /PID %%a >nul 2>&1
timeout /t 2 /nobreak >nul

REM ── Install backend dependencies ─────────────────────────
echo  Installing backend dependencies...
cd /d "%~dp0backend"
pip install -r requirements.txt --quiet

REM ── Start Backend in its own visible window ───────────────
echo  Starting Backend (port 8000)...
start "TalentScout BACKEND :8000" cmd /k "color 0B && echo. && echo  [BACKEND] TalentScout AI API && echo  http://localhost:8000 && echo  http://localhost:8000/docs && echo. && cd /d "%~dp0backend" && python -m uvicorn main:app --reload --port 8000"

REM ── Wait for backend to be ready ─────────────────────────
echo  Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM ── Install frontend dependencies ────────────────────────
echo  Installing frontend dependencies...
cd /d "%~dp0frontend"
call npm install --silent

REM ── Start Frontend in its own visible window ─────────────
echo  Starting Frontend (port 5173)...
start "TalentScout FRONTEND :5173" cmd /k "color 0D && echo. && echo  [FRONTEND] TalentScout AI UI && echo  http://localhost:5173 && echo. && cd /d "%~dp0frontend" && node node_modules\vite\bin\vite.js"

REM ── Wait and open browser ────────────────────────────────
echo  Waiting for frontend to start...
timeout /t 8 /nobreak >nul

echo.
echo  ==========================================
echo   Both servers are running!
echo.
echo   Frontend :  http://localhost:5173
echo   Backend  :  http://localhost:8000
echo   API Docs :  http://localhost:8000/docs
echo  ==========================================
echo.
echo  Opening browser...
start "" "http://localhost:5173"

echo.
echo  Keep this window open while using the app.
echo  Close the BACKEND and FRONTEND windows to stop servers.
echo.
pause
