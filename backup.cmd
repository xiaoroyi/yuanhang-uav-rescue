@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Project environment is missing. Run setup.cmd first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" scripts\backup.py %*
set "YUANHANG_BACKUP_EXIT=%errorlevel%"
if "%~1"=="" pause
exit /b %YUANHANG_BACKUP_EXIT%
