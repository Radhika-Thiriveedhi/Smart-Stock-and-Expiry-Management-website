@echo off
title StockWise — Generate 500,000+ Lines of Enterprise Code
cd /d "%~dp0\StockWise"

echo ========================================================
echo   StockWise — Production Application Code Builder
echo   Target: 500,000+ Prod LOC (Excludes tests/generated)
echo ========================================================
echo.

python build_app_code.py

echo.
pause
