@echo off
setlocal
cd /d "%~dp0"
py -3.11 scripts\setup.py
if errorlevel 1 pause
