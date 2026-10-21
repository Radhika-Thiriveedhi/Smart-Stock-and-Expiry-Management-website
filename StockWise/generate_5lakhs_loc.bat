@echo off
title StockWise — Generate 500,000+ Lines of Enterprise Code
cd /d "%~dp0"

echo ========================================================
echo   StockWise — Enterprise Codebase Expansion (5 Lakhs LOC)
echo ========================================================
echo.
echo This tool generates 500,000+ lines of valid enterprise
echo algorithms, retail FMCG registries, tax compliance engines,
echo and test matrices without modifying or slowing down the website.
echo.
echo Starting builder...
echo.

python build_app_code.py

echo.
pause
