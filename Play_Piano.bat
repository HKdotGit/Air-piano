@echo off
title Virtual Air Piano
echo ==========================================
echo       Starting Virtual Air Piano...
echo ==========================================
echo.

:: Automatically install cv2 (opencv-python) if missing
echo Checking dependencies...
python -m pip install opencv-python --quiet
echo Dependencies ready!

echo.
echo Please wait while the game and camera load...
:: Run the main game
python main.py

pause
