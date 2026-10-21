@echo off
title StockWise — Build 500,000+ Prod LOC
cd /d "%~dp0\StockWise"

echo ========================================================
echo   StockWise — Production Code Scale Builder
echo   Target: 500,000+ Prod LOC (Excludes tests/generated)
echo ========================================================
echo.

python build_app_code.py

echo.
pause
