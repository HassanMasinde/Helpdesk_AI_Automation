@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found.
    echo Create it first with:
    echo   python -m venv .venv
    echo   .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo Starting Helpdesk AI Dashboard...
start "" cmd /c "timeout /t 2 >nul & start "" http://127.0.0.1:8790"
".venv\Scripts\python.exe" -u dashboard_server.py
pause
