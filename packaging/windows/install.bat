@echo off
REM migasfree-agent installer for Windows
REM Run this script as Administrator

setlocal EnableDelayedExpansion

set "INSTALL_DIR=%PROGRAMDATA%\migasfree-agent"
set "AGENT_SCRIPT=migasfree-agent"
set "SERVICE_NAME=migasfree-agent"

echo.
echo ========================================
echo   Migasfree Agent Installer for Windows
echo ========================================
echo.

REM Check for Administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script requires Administrator privileges.
    echo Right-click and select "Run as administrator".
    pause
    exit /b 1
)

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.6+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Checking Python version...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo       Python %PYTHON_VERSION% found.

echo.
echo [2/5] Installing Python dependencies...
pip install --upgrade requests websockets migasfree-client
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [3/5] Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo.
echo [4/5] Copying agent script...
copy /Y "%~dp0%AGENT_SCRIPT%" "%INSTALL_DIR%\%AGENT_SCRIPT%" >nul
if %errorlevel% neq 0 (
    echo ERROR: Failed to copy agent script.
    pause
    exit /b 1
)

echo.
echo [5/5] Creating Windows Service...
REM Check if NSSM is available
where nssm >nul 2>&1
if %errorlevel% equ 0 (
    echo       Using NSSM to create service...
    nssm stop %SERVICE_NAME% >nul 2>&1
    nssm remove %SERVICE_NAME% confirm >nul 2>&1
    nssm install %SERVICE_NAME% python "%INSTALL_DIR%\%AGENT_SCRIPT%"
    nssm set %SERVICE_NAME% AppDirectory "%INSTALL_DIR%"
    nssm set %SERVICE_NAME% DisplayName "Migasfree Agent"
    nssm set %SERVICE_NAME% Description "Multi-protocol TCP tunnel agent for remote access"
    nssm set %SERVICE_NAME% Start SERVICE_AUTO_START
    nssm set %SERVICE_NAME% AppStdout "%INSTALL_DIR%\agent.log"
    nssm set %SERVICE_NAME% AppStderr "%INSTALL_DIR%\agent.log"
    nssm set %SERVICE_NAME% AppRotateFiles 1
    nssm set %SERVICE_NAME% AppRotateBytes 1048576
    echo       Service created successfully.
    echo.
    echo To start the service, run:
    echo   nssm start %SERVICE_NAME%
) else (
    echo       NSSM not found. Creating scheduled task instead...
    schtasks /create /tn "%SERVICE_NAME%" /tr "python \"%INSTALL_DIR%\%AGENT_SCRIPT%\"" /sc onstart /ru SYSTEM /f >nul 2>&1
    if %errorlevel% equ 0 (
        echo       Scheduled task created successfully.
        echo.
        echo To start the agent now, run:
        echo   schtasks /run /tn %SERVICE_NAME%
    ) else (
        echo       WARNING: Could not create scheduled task.
        echo       You can run the agent manually:
        echo         python "%INSTALL_DIR%\%AGENT_SCRIPT%"
    )
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Installation directory: %INSTALL_DIR%
echo.
echo IMPORTANT: Make sure migasfree-client is configured before starting the agent.
echo Configuration file: %PROGRAMDATA%\migasfree-client\migasfree.conf
echo.
pause
