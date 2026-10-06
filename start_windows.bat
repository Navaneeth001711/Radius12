@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (set PY=py) else (set PY=python)
if not exist venv (
  echo Creating Python virtual environment...
  %PY% -m venv venv || goto :error
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt || goto :error
python start.py
goto :eof
:error
echo.
echo Setup failed. Make sure Python 3.10+ is installed and internet access is available for the first dependency install.
pause
