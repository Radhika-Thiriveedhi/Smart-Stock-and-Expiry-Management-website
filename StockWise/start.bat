@echo off
title StockWise — Smart Stock & Expiry Management
cd /d "%~dp0"

echo ========================================================
echo   StockWise — Smart Stock & Expiry Management
echo ========================================================
echo.

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python was not found in your system PATH.
    echo Please ensure Python 3.8+ is installed.
    echo.
    pause
    exit /b 1
)

echo [2/3] Verifying dependencies (Flask, Werkzeug)...
python -m pip install -r requirements.txt --quiet --disable-pip-version-check

if not exist "app\services\enterprise\demand_forecasting_service_001.py" (
    echo [*] Initializing Enterprise Production Codebase (500,000+ Prod LOC)...
    python build_app_code.py
)

echo [3/3] Starting StockWise server on http://127.0.0.1:5000 ...
echo.
echo ========================================================
echo   Demo Logins:
echo     - Owner:    owner    / owner123
echo     - Manager:  manager  / manager123
echo     - Employee: employee / employee123
echo ========================================================
echo.
echo Opening browser...
start "" "http://127.0.0.1:5000"
echo.
python run.py

pause
