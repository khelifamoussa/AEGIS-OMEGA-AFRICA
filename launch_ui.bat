@echo off
cd /d "%~dp0"
title AEGIS OMEGA AFRICA
echo Starting AEGIS OMEGA AFRICA...
start "" "http://127.0.0.1:8765"
python app_server.py
if errorlevel 1 (
  echo.
  echo ERROR: AEGIS could not start.
  echo Confirm that Python and aegis_v8.py are in this folder.
  pause
)
