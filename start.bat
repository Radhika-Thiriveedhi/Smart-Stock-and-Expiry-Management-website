@echo off
title StockWise — Smart Stock & Expiry Management
cd /d "%~dp0\StockWise"

echo ========================================================
echo   StockWise — Smart Stock & Expiry Management
echo ========================================================
echo.

if not exist "app\services\enterprise\demand_forecasting_service_001.py" (
    echo [*] Initializing Enterprise Production Codebase (500,000+ Prod LOC)...
    python build_app_code.py
)

echo Starting StockWise server on http://127.0.0.1:5000 ...
echo.
start "" "http://127.0.0.1:5000"
python run.py

pause
