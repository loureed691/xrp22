@echo off
REM Run the demo

echo ============================================================
echo XRP Hedge Bot - Demo Mode
echo ============================================================
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [WARNING] Virtual environment not found
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Run demo
python demo.py

echo.
pause
