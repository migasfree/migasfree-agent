@echo off
REM migasfree-agent uninstaller for Windows
REM Run this script as Administrator

setlocal EnableDelayedExpansion

set "INSTALL_DIR=%PROGRAMDATA%\migasfree-agent"
set "SERVICE_NAME=migasfree-agent"

echo.
echo ==========================================
echo   Migasfree Agent Uninstaller for Windows
echo ==========================================
echo.

REM Check for Administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script requires Administrator privileges.
    echo Right-click and select "Run as administrator".
    pause
    exit /b 1
)

echo [1/3] Stopping service/task...
where nssm >nul 2>&1
if %errorlevel% equ 0 (
    nssm stop %SERVICE_NAME% >nul 2>&1
    nssm remove %SERVICE_NAME% confirm >nul 2>&1
    echo       NSSM service removed.
) else (
    schtasks /end /tn %SERVICE_NAME% >nul 2>&1
    schtasks /delete /tn %SERVICE_NAME% /f >nul 2>&1
    echo       Scheduled task removed.
)

echo.
echo [2/3] Removing installation directory...
if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%"
    echo       Directory removed.
) else (
    echo       Directory not found, skipping.
)

echo.
echo [3/3] Done.
echo.
echo ==========================================
echo   Uninstallation Complete!
echo ==========================================
echo.
echo NOTE: Python dependencies were not removed.
echo If you want to remove them, run:
echo   pip uninstall requests websockets migasfree-client
echo.
pause
