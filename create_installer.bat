@echo off
setlocal EnableDelayedExpansion
title CREATE INSTALLER - Project IDE Opener
color 0A
echo ===================================================
echo   CREATE WINDOWS INSTALLER (1-Click)
echo   Project IDE Opener v2.0 Modern
echo ===================================================
echo.

REM --- Cek Python & PyInstaller ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan! Install dari https://python.org
    pause & exit /b 1
)
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] PyInstaller belum ada, menginstall...
    pip install pyinstaller
)

REM --- Step 1: Build EXE Portable ---
echo.
echo [1/3] Building EXE portable...
if exist "logo.ico" (
    pyinstaller --onefile --windowed --name "ProjectIDEOpener" --icon=logo.ico --add-data "logo.ico;." --add-data "logo.png;." --clean main.py
) else (
    pyinstaller --onefile --windowed --name "ProjectIDEOpener" --clean main.py
)
if not exist "dist\ProjectIDEOpener.exe" (
    echo [ERROR] Gagal build EXE!
    pause & exit /b 1
)
echo [OK] EXE: dist\ProjectIDEOpener.exe

REM --- Step 2: Cek Inno Setup, auto-download jika belum ada ---
echo.
echo [2/3] Mengecek Inno Setup Compiler...
set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "%ISCC%" goto COMPILE

echo [INFO] Inno Setup belum terinstall.
echo        Akan download & install otomatis (butuh internet)...
choice /M "Download Inno Setup 6 sekarang"
if %errorlevel% neq 1 goto NOINNO

set "INNO_TMP=%TEMP%\is6setup.exe"
echo Downloading Inno Setup...
powershell -Command "Invoke-WebRequest -Uri 'https://jrsoftware.org/download.php/is.exe' -OutFile '%INNO_TMP%'"
if not exist "%INNO_TMP%" (
    echo [ERROR] Download gagal. Download manual: https://jrsoftware.org/isdl.php
    pause & exit /b 1
)
echo Installing Inno Setup (silent)...
"%INNO_TMP%" /SP- /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
timeout /t 5 >nul
if not exist "%ISCC%" (
    echo [ERROR] Install gagal. Coba manual dari https://jrsoftware.org/isdl.php
    pause & exit /b 1
)
echo [OK] Inno Setup terinstall.

:COMPILE
echo.
echo [3/3] Compile installer.iss -> Setup.exe
"%ISCC%" "installer.iss"
if %errorlevel% neq 0 (
    echo [ERROR] Compile installer gagal! Cek installer.iss
    pause & exit /b 1
)

echo.
echo ===================================================
echo   SUKSES! INSTALLER SIAP
echo ===================================================
for %%F in (dist\ProjectIDEOpener-Setup*.exe) do (
    echo   File: %%F
    echo   Size: %%~zF bytes
)
echo.
echo Fitur installer:
echo  - Wizard Next-Next-Finish (Modern)
echo  - Icon logo.ico
echo  - Start Menu + Desktop shortcut (opsional)
echo  - Uninstall via Settings ^> Apps
echo  - Install path: %LOCALAPPDATA%\Programs\Project IDE Opener\
echo.
choice /M "Buka folder dist dan jalankan installer"
if %errorlevel% equ 1 (
    explorer dist
    start "" "dist\ProjectIDEOpener-Setup-v2.0.exe"
)
pause
exit /b 0

:NOINNO
echo.
echo [INFO] Skip installer. EXE portable tetap tersedia:
echo   dist\ProjectIDEOpener.exe
echo   File ini bisa langsung dipakai tanpa install.
explorer dist
pause
