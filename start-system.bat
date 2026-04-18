@echo off
echo ========================================
echo   Student Attendance System Launcher
echo ========================================
echo.

echo [1/4] Checking MongoDB...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] MongoDB is running
) else (
    echo [ERROR] MongoDB is NOT running!
    echo Please start MongoDB first
    pause
    exit /b 1
)

echo.
echo [2/4] Testing camera...
cd backend
python test_camera.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Camera test failed!
    echo Please close other apps using the camera
    pause
    exit /b 1
)

echo.
echo [3/4] Starting Backend...
start "Attendance Backend" cmd /k "uvicorn app.main:app --reload"
timeout /t 5 /nobreak >nul

echo.
echo [4/4] Starting Frontend...
cd ..\frontend
start "Attendance Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo   System Started Successfully!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5174
echo API Docs: http://localhost:8000/docs
echo.
echo Login: admin / admin123
echo.
echo Press any key to open the application...
pause >nul

start http://localhost:5174

echo.
echo To stop the system, close both terminal windows
echo.
pause
