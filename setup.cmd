@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" scripts\setup.py %*
  goto finish
)
py -3.11 -c "import sys; sys.exit(sys.version_info[:2] != (3, 11))" >nul 2>&1
if not errorlevel 1 (
  py -3.11 scripts\setup.py %*
  goto finish
)
py -3.12 -c "import sys; sys.exit(sys.version_info[:2] != (3, 12))" >nul 2>&1
if not errorlevel 1 (
  py -3.12 scripts\setup.py %*
  goto finish
)
python -c "import sys; sys.exit(not ((3, 11) <= sys.version_info[:2] < (3, 13)))" >nul 2>&1
if not errorlevel 1 (
  python scripts\setup.py %*
  goto finish
)
echo Compatible Python was not found. Install Python 3.11 or 3.12, then run setup.cmd again.
pause
exit /b 1
:finish
set "YUANHANG_SETUP_EXIT=%errorlevel%"
if "%~1"=="" pause
exit /b %YUANHANG_SETUP_EXIT%
