@echo off
title Build Installer - VS Code Folder Opener
color 0A
echo ===================================================
echo   BUILD INSTALLER WINDOWS (.exe Setup)
echo ===================================================
echo.

REM Step 1: Build .exe via PyInstaller
echo [1/3] Building EXE...
if exist logo.ico (
    pyinstaller --onefile --windowed --name "VSCodeOpener-Modern" --icon=logo.ico --clean main.py
) else (
    pyinstaller --onefile --windowed --name "VSCodeOpener-Modern" --clean main.py
)
if not exist "dist\VSCodeOpener-Modern.exe" (
    echo [ERROR] EXE gagal dibuat!
    pause
    exit /b 1
)
echo [OK] EXE siap: dist\VSCodeOpener-Modern.exe
echo.

REM Step 2: Cek Inno Setup
echo [2/3] Mengecek Inno Setup...
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
    echo [WARNING] Inno Setup tidak ditemukan di %ISCC%
    echo Download dari: https://jrsoftware.org/isdl.php
    echo.
    echo Alternatif: EXE portable sudah siap di dist\ tanpa installer.
    echo Ingin buka folder dist?
    choice /M "Buka folder dist"
    if %errorlevel% equ 1 explorer dist
    pause
    exit /b 0
)

REM Step 3: Compile installer
echo [3/3] Compile installer.iss ...
%ISCC% "installer.iss"
if %errorlevel% neq 0 (
    echo [ERROR] Compile installer gagal!
    pause
    exit /b 1
)

echo.
echo ===================================================
echo   SUKSES! Installer ada di: dist\VSCodeOpener-Setup-v2.0.exe
echo ===================================================
dir dist\VSCodeOpener-Setup*.exe | findstr VSCodeOpener
echo.
echo Installer ini bisa:
echo  - Next-Next-Finish wizard
echo  - Buat Start Menu + Desktop shortcut (opsional)
echo  - Uninstall via Control Panel / Settings
echo.
explorer dist
pause
