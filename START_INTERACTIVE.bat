@echo off
REM Start Velocity Interactive Mode
REM Double-click to run!

echo ======================================================================
echo VELOCITY - INTERACTIVE MODE
echo ======================================================================
echo.
echo Starting Velocity...
echo.

cd /d "%~dp0"

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run interactive mode
python interactive_velocity.py

pause
