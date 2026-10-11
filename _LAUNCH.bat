@echo off
setlocal
title IRIS Launcher

REM ---- ensure X: mapped ----
if exist X:\00_python\python.exe goto :ready
echo [IRIS] X: not mapped. Trying subst...
subst X: "%~dp0"
if not exist X:\00_python\python.exe (
  echo [IRIS] ERROR: X:\00_python\python.exe not found.
  echo [IRIS] Put this file on the SSD root and try again.
  pause
  exit /b 1
)

:ready
echo [IRIS] SSD mounted as X:

REM ---- bootstrap check ----
echo [IRIS] Checking dependencies...
X:\00_python\python.exe X:\bootstrap.py --check
if errorlevel 1 (
  echo [IRIS] Bootstrap failed. See X:\93_logs\bootstrap.log
  pause
  exit /b 1
)

REM ---- launch UI ----
echo [IRIS] Launching UI...
start "" http://localhost:8501
X:\00_python\python.exe -m streamlit run X:\90_ui\app_v4.py

pause