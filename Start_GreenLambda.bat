@echo off
title GreenLambda Application Launcher
echo ===================================================
echo     Starting GreenLambda: From Code to Carbon
echo ===================================================
echo.

REM Check if backend\.env exists
if not exist "backend\.env" (
    echo [WARNING] backend\.env not found!
    echo Please create backend\.env with required keys.
    echo See backend\.env.example for reference.
    echo.
    pause
    exit /b 1
)
echo [OK] Environment file found.

echo [1/3] Launching the Machine Learning Backend Server...
cd /d "%~dp0"
start "GreenLambda Backend" cmd /k "cd backend && ..\ml_model\venv\Scripts\python.exe app.py"

echo [2/3] Starting benchmark warm-up invocations (runs once)...
start "GreenLambda Invocations" cmd /c "cd backend && ..\ml_model\venv\Scripts\python.exe invoke_benchmarks.py"

echo [3/3] Opening the UI in your default browser...
:: Wait 3 seconds to let Python load up the Machine Learning Models
timeout /t 3 /nobreak >nul
start "" "%~dp0index.html"

echo.
echo Success! GreenLambda is running.
echo The Backend server will automatically shut down and close its window
echo when you close the website (all browser tabs).
echo.
echo You can close this launcher terminal now. Have a great demo!
exit
