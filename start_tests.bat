@echo off
title StockWise Unit Tests
cd /d "%~dp0"

echo ========================================================
echo   Running StockWise Unit Test Suite
echo ========================================================
echo.

python StockWise\tests\run_all_tests.py
if %errorlevel% neq 0 (
    python tests\run_all_tests.py
)

echo.
pause
