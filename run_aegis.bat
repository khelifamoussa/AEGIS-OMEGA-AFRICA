@echo off
setlocal
cd /d "%~dp0"
title AEGIS OMEGA AFRICA V8

echo ============================================================
echo AEGIS OMEGA AFRICA V8
echo Offline Deterministic Crisis Decision-Support
echo ============================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python was not found in PATH.
    echo Install Python 3.10+ or add Python to PATH, then retry.
    echo.
    pause
    exit /b 1
)

python aegis_v8.py
set "AEGIS_EXIT=%ERRORLEVEL%"

echo.
if not "%AEGIS_EXIT%"=="0" (
    echo AEGIS exited with code %AEGIS_EXIT%.
) else (
    echo AEGIS run completed.
)
echo.
pause
exit /b %AEGIS_EXIT%
