@echo off
title StockWise — Codebase Line Counter
cd /d "%~dp0"
python verify_loc.py
echo.
pause
