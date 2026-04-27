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
echo  [1/5] Cleaning up old processes...
taskkill /F /IM uvicorn.exe >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 " 2^>nul') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173 " 2^>nul') do taskkill /F /PID %%a >nul 2>&1
timeout /t 2 /nobreak >nul

REM ── Install backend dependencies (skip if already installed) ──
echo  [2/5] Checking backend dependencies...
cd /d "%~dp0backend"
pip install -r requirements.txt --quiet --no-warn-script-location

REM ── Start Backend in its own visible window ───────────────
echo  [3/5] Starting Backend (port 8000)...
start "TalentScout BACKEND :8000" cmd /k "color 0B && echo. && echo  ====================================== && echo   TalentScout AI - BACKEND SERVER && echo   http://localhost:8000 && echo   API Docs: http://localhost:8000/docs && echo  ====================================== && echo. && cd /d "%~dp0backend" && python -m uvicorn main:app --reload --port 8000"

REM ── Wait for backend to be ready (poll up to 30s) ────────
echo  [4/5] Waiting for backend to start...
set /a tries=0
:waitloop
timeout /t 2 /nobreak >nul
set /a tries+=1
curl -s -o nul -w "%%{http_code}" http://localhost:8000/health 2>nul | findstr "200" >nul
if %errorlevel%==0 (
  echo   Backend is ready!
  goto backendready
)
if %tries% LSS 15 goto waitloop
echo   Backend took too long - continuing anyway...
:backendready

REM ── Install frontend dependencies (skip if node_modules exists) ──
echo  [5/5] Starting Frontend (port 5173)...
cd /d "%~dp0frontend"
if not exist "node_modules\" (
  echo   Installing frontend dependencies...
  call npm install --silent
)

REM ── Start Frontend in its own visible window ─────────────
start "TalentScout FRONTEND :5173" cmd /k "color 0D && echo. && echo  ====================================== && echo   TalentScout AI - FRONTEND SERVER && echo   http://localhost:5173 && echo  ====================================== && echo. && cd /d "%~dp0frontend" && node node_modules\vite\bin\vite.js"

REM ── Wait for frontend then open browser ──────────────────
timeout /t 5 /nobreak >nul

echo.
echo  ==========================================
echo   BOTH SERVERS ARE RUNNING!
echo.
echo   Frontend :  http://localhost:5173
echo   Backend  :  http://localhost:8000
echo   API Docs :  http://localhost:8000/docs
echo  ==========================================
echo.

start "" "http://localhost:5173"

echo.
echo  Keep this window open while using the app.
echo  Close the BACKEND / FRONTEND windows to stop servers.
echo.
pause
