@echo off
setlocal
cd /d "%~dp0"
title Image Recognition App - Google Cloud Vision

if not exist ".venv\Scripts\python.exe" (
    echo [1/2] Creating virtual environment...
    py -m venv .venv 2>nul
    if errorlevel 1 python -m venv .venv
    if not exist ".venv\Scripts\python.exe" (
        echo ERROR: Python was not found. Install Python 3.10+ and try again.
        pause
        exit /b 1
    )
)

if not exist ".venv\Scripts\streamlit.exe" (
    echo [2/2] Installing dependencies...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Could not install dependencies.
        pause
        exit /b 1
    )
)

if not exist "%USERPROFILE%\.streamlit" mkdir "%USERPROFILE%\.streamlit" >nul 2>&1
if not exist "%USERPROFILE%\.streamlit\credentials.toml" (
    echo [general]> "%USERPROFILE%\.streamlit\credentials.toml"
    echo email = "">> "%USERPROFILE%\.streamlit\credentials.toml"
)

if not exist ".streamlit\secrets.toml" (
    echo WARNING: .streamlit\secrets.toml was not found.
    echo Add your Google Cloud service account key before analyzing images.
    echo.
)

echo Starting the app at http://localhost:8501 ...
echo Close this window or press Ctrl+C to stop the app.
echo.
".venv\Scripts\python.exe" -m streamlit run app.py --browser.gatherUsageStats=false

if errorlevel 1 (
    echo.
    echo The app stopped with an error.
    pause
)

endlocal
