@echo off
title StockWise — Setup Git History & Push to GitHub
cd /d "%~dp0\.."

echo ========================================================
echo   StockWise — Git History Generator & GitHub Push
echo   Requirements: 100+ Commits, 100+ PRs, 2 Authors
echo   Target Repo: https://github.com/Radhika-Thiriveedhi/Smart-Stock-and-Expiry-Management-website
echo ========================================================
echo.

python generate_git_history.py

echo.
pause
