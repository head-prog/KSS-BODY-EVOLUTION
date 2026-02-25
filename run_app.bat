@echo off
REM Body Evolution Wellness System Launcher
title Body Evolution - Wellness Evaluation System

echo.
echo ========================================
echo Body Evolution Wellness System
echo ========================================
echo.

REM Activate venv and run app
cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Starting Streamlit app...
    echo.
    streamlit run app.py
) else (
    echo ERROR: Virtual environment not found!
    echo Please run setup.ps1 first
    pause
)
