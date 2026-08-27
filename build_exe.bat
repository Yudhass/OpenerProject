@echo off
title Build EXE - VS Code Folder Opener
echo ===================================================
echo   BUILD .EXE - VS Code Folder Opener
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
    pyinstaller --onefile --windowed --name "VSCodeOpener-Modern" --icon=logo.ico --clean main.py
) else (
    pyinstaller --onefile --windowed --name "VSCodeOpener-Modern" --clean main.py
)

echo.
if exist "dist\VSCodeOpener.exe" (
    echo ===================================================
    echo   SUKSES! File ada di: dist\VSCodeOpener.exe
    echo   Ukuran:
    dir "dist\VSCodeOpener.exe" | findstr "VSCodeOpener"
    echo.
    echo   File ini bisa dikopikan ke komputer Windows lain
    echo   tanpa perlu install Python!
    echo ===================================================
    explorer dist
) else (
    echo [ERROR] Build gagal. Cek log di atas.
)
pause
