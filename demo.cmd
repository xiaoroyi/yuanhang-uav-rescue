@echo off
setlocal
if not exist "%~dp0deliverables\yuanhang-demo.html" (
  echo Demo material is missing. See deliverables\README.md.
  pause
  exit /b 1
)
start "" "%~dp0deliverables\yuanhang-demo.html"
