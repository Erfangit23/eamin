@echo off
title XAU Trader Bot - Installer
cd /d "%~dp0"

echo ========================================
echo   XAU Trader Bot - Installation
echo ========================================
echo.

echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Edit config.json with your credentials:
echo      - Telegram api_id, api_hash, phone
echo      - Report bot token
echo      - MT5 login, password, server
echo      - Your Telegram user ID (authorized_user_ids)
echo   2. Make sure MetaTrader 5 is installed and running
echo   3. Run start.bat to start the bot
echo   4. On first run, enter the Telegram code sent to your phone
echo.
pause
