@echo off
REM migasfree-agent build script for Windows
REM Creates a distributable package

setlocal EnableDelayedExpansion

set "PROJECT_ROOT=%~dp0"
set "VERSION=%~1"
if "%VERSION%"=="" set "VERSION=1.0.0"

set "WIN_DIR=packaging\windows"
set "DIST_DIR=dist"

echo.
echo ========================================
echo   Building Migasfree Agent v%VERSION%
echo ========================================
echo.

REM Create dist directory
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

REM Create build directory
set "BUILD_DIR=%DIST_DIR%\migasfree-agent-%VERSION%"
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
mkdir "%BUILD_DIR%"

echo [1/4] Copying agent script...
copy /Y "agent\migasfree-agent" "%BUILD_DIR%\migasfree-agent" >nul
if %errorlevel% neq 0 (
    echo ERROR: Failed to copy agent script.
    exit /b 1
)

echo [2/4] Copying installation scripts...
copy /Y "%WIN_DIR%\install.bat" "%BUILD_DIR%\" >nul
copy /Y "%WIN_DIR%\uninstall.bat" "%BUILD_DIR%\" >nul

echo [3/4] Copying documentation...
copy /Y "README.md" "%BUILD_DIR%\" >nul
copy /Y "LICENSE" "%BUILD_DIR%\" >nul 2>nul

echo [4/4] Creating ZIP package...
REM Check if PowerShell is available for compression
where powershell >nul 2>&1
if %errorlevel% equ 0 (
    set "ZIP_FILE=%DIST_DIR%\migasfree-agent-%VERSION%-windows.zip"
    if exist "!ZIP_FILE!" del "!ZIP_FILE!"
    powershell -Command "Compress-Archive -Path '%BUILD_DIR%\*' -DestinationPath '!ZIP_FILE!'" >nul
    if %errorlevel% equ 0 (
        echo       Created: !ZIP_FILE!
    ) else (
        echo       WARNING: Failed to create ZIP file.
    )
) else (
    echo       PowerShell not found. Skipping ZIP creation.
    echo       Package files are in: %BUILD_DIR%
)

echo.
echo ========================================
echo   Build Complete!
echo ========================================
echo.
echo Package contents in: %BUILD_DIR%
dir /b "%BUILD_DIR%"
echo.
