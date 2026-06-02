@echo off
chcp 65001 >nul
cd /d "%~dp0.."
if not exist "%~dp0.venv\Scripts\pythonw.exe" (
    echo Окружение .venv не найдено. Сначала запустите install.bat
    pause
    exit /b 1
)
start "" /min "%~dp0.venv\Scripts\pythonw.exe" -m voicekey.main
