@echo off
echo ======================================================================
echo VELOCITY - INTERACTIVE MODE
echo ======================================================================
echo.
echo Starting Velocity interactive shell...
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat
python interactive_velocity.py

pause
