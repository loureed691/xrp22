@echo off
REM Run the XRP Hedge Bot

echo ============================================================
echo XRP Hedge Bot - Starting
echo ============================================================
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [WARNING] Virtual environment not found
    echo Run setup.bat first!
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo [ERROR] .env file not found
    echo Please copy .env.example to .env and configure your API keys
    pause
    exit /b 1
)

REM Run validation first
echo Running setup validation...
python validate_setup.py
if errorlevel 1 (
    echo.
    echo [ERROR] Validation failed. Please fix the issues above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Starting bot...
echo Press Ctrl+C to stop
echo ============================================================
echo.

REM Run the bot
python bot.py

echo.
echo Bot stopped.
pause
