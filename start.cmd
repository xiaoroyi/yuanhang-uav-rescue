@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Project Python environment is missing. Run setup.cmd first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" "scripts\launch.py" --open
if errorlevel 1 pause
