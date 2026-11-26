@echo off
title Build EXE - Project IDE Opener
echo ===================================================
echo   BUILD .EXE - Project IDE Opener
echo ===================================================
echo.

REM Cek pyinstaller
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller belum terinstall. Installing...
    pip install pyinstaller
)

echo.
echo Building...
if exist logo.ico (
    echo Menggunakan icon: logo.ico
    pyinstaller --onefile --windowed --name "ProjectIDEOpener" --icon=logo.ico --add-data "logo.ico;." --add-data "logo.png;." --clean main.py
) else (
    pyinstaller --onefile --windowed --name "ProjectIDEOpener" --clean main.py
)

echo.
if exist "dist\ProjectIDEOpener.exe" (
    echo ===================================================
    echo   SUKSES! File ada di: dist\ProjectIDEOpener.exe
    echo   Ukuran:
    dir "dist\ProjectIDEOpener.exe" | findstr "ProjectIDEOpener"
    echo.
    echo   File ini bisa dikopikan ke komputer Windows lain
    echo   tanpa perlu install Python!
    echo ===================================================
    explorer dist
) else (
    echo [ERROR] Build gagal. Cek log di atas.
)
pause
