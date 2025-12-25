@echo off
SETLOCAL EnableDelayedExpansion

REM --- Configuration ---
SET VENV_DIR=.venv
SET SCRIPT_NAME=cisdownloader.py
SET REQUIREMENTS=requirements.txt

REM --- Check for Python ---
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM --- Create Virtual Environment if it doesn't exist ---
IF NOT EXIST "%VENV_DIR%" (
    echo [INFO] Creating virtual environment in %VENV_DIR%...
    python -m venv %VENV_DIR%
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [INFO] Virtual environment created.
)

REM --- Activate Virtual Environment ---
CALL "%VENV_DIR%\Scripts\activate.bat"

REM --- Install Dependencies ---
IF EXIST "%REQUIREMENTS%" (
    echo [INFO] Checking/Installing dependencies...
    pip install -r %REQUIREMENTS%
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
) ELSE (
    echo [WARNING] %REQUIREMENTS% not found. Skipping dependency installation.
)

REM --- Run the Script ---
echo.
echo [INFO] Running %SCRIPT_NAME%...
echo.
python %SCRIPT_NAME%

REM --- Deactivate and Exit ---
deactivate
echo.
echo [INFO] Done.
pause
