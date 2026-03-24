@echo off
title GreenLambda Application Launcher
echo ===================================================
echo     Starting GreenLambda: From Code to Carbon
echo ===================================================
echo.
echo [1/2] Launching the Machine Learning Backend Server...
cd /d "%~dp0"
start cmd /k "cd backend && ..\ml_model\venv\Scripts\activate.bat && python app.py"

echo [2/2] Opening the UI in your default browser...
:: Wait 3 seconds to let Python load up the Machine Learning Models
timeout /t 3 /nobreak >nul
start "" "%~dp0index.html"

echo.
echo Success! GreenLambda is running.
echo You can close this terminal. Have a great demo!
exit
