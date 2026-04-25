@echo off
echo Starting TalentScout AI Pipeline...

echo Installing backend dependencies...
cd backend
pip install -r requirements.txt

echo Starting Backend Server...
start cmd /k "uvicorn main:app --reload --port 8000"

echo Installing frontend dependencies...
cd ../frontend
call npm install

echo Starting Frontend Server...
start cmd /k "node node_modules\vite\bin\vite.js"

echo.
echo ========================================================
echo Servers are starting up!
echo Frontend will be available at: http://localhost:5173
echo Backend will be available at:  http://localhost:8000
echo ========================================================
pause
