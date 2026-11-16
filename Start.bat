@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 goto failed
)
if not exist ".venv\installed.ok" (
  .venv\Scripts\python.exe -m pip install -r requirements.txt
  if errorlevel 1 goto failed
  echo installed>.venv\installed.ok
)
if exist "credentials.json" set "GOOGLE_APPLICATION_CREDENTIALS=%~dp0credentials.json"
.venv\Scripts\python.exe -m streamlit run app.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo.
echo Setup or startup failed. Check your internet connection and Python installation.
pause
exit /b 1
