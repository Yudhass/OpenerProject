@echo off
title VS Code Folder Opener
REM Jalankan aplikasi tanpa perlu install apa pun
python "%~dp0main.py"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Gagal menjalankan aplikasi.
    echo Coba jalankan: python main.py
    pause
)
