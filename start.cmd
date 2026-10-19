@echo off
setlocal
cd /d "%~dp0"
if exist "portable-python\python.exe" goto portable
if not exist ".venv\Scripts\python.exe" (
  echo Project Python environment is missing. Run setup.cmd first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" "scripts\launch.py" --open %*
set "YUANHANG_EXIT=%errorlevel%"
if not "%YUANHANG_EXIT%"=="0" pause
exit /b %YUANHANG_EXIT%

:portable
set "PYTHONHOME="
set "PYTHONPATH="
set "PYTHONNOUSERSITE=1"
set "PYTHONIOENCODING=utf-8"
set "PATH=%CD%\portable-python;%CD%\portable-python\DLLs;%PATH%"
"portable-python\python.exe" -B "scripts\launch.py" --open %*
set "YUANHANG_EXIT=%errorlevel%"
if not "%YUANHANG_EXIT%"=="0" pause
exit /b %YUANHANG_EXIT%
