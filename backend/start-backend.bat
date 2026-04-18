@echo off
echo ========================================
echo   Starting Attendance System Backend
echo ========================================
echo.

echo [1/2] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [2/2] Starting backend server...
echo.
echo Backend will run at: http://localhost:8000
echo API Docs at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

uvicorn app.main:app --reload
