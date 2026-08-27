@echo off
title Install - VS Code Folder Opener
color 0A
echo ===================================================
echo   VS CODE FOLDER OPENER - INSTALLER
echo ===================================================
echo.

REM Cek Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan!
    echo.
    echo Silahkan install Python 3.8+ dari:
    echo https://www.python.org/downloads/
    echo.
    echo Pastikan centang "Add python.exe to PATH" saat install.
    pause
    exit /b 1
)

echo [OK] Python ditemukan:
python --version

echo.
echo [OK] Mengecek tkinter (bawaan Python)...
python -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] tkinter tidak tersedia. Reinstall Python dengan opsi Tcl/Tk.
    pause
    exit /b 1
)
echo [OK] tkinter siap.

echo.
echo [OK] Mengecek VS Code...
where code >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] VS Code terdeteksi di PATH:
    where code
) else (
    echo [WARNING] VS Code tidak di PATH.
    echo Aplikasi tetap jalan, tapi akan cari di:
    echo   C:\Program Files\Microsoft VS Code\bin\code.cmd
    echo   %%LOCALAPPDATA%%\Programs\Microsoft VS Code\bin\code.cmd
    echo.
    echo Jika belum install VS Code, download di:
    echo   https://code.visualstudio.com/
)

echo.
echo ---------------------------------------------------
echo Tidak perlu pip install! Aplikasi pakai stdlib saja.
echo ---------------------------------------------------
echo.
echo OPSIONAL: Install PyInstaller untuk build .exe ?
echo.
choice /M "Install PyInstaller sekarang"
if %errorlevel% equ 1 (
    echo.
    echo Installing pyinstaller...
    pip install pyinstaller
    echo.
    echo [OK] PyInstaller siap. Build dengan: build_exe.bat
)

echo.
echo ===================================================
echo   INSTALASI SELESAI! Jalankan: run.bat
echo ===================================================
pause
