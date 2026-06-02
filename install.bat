@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ============================================
echo    VoiceKey - установка (Windows)
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден в PATH.
    echo Установите Python 3.11 или 3.12: https://www.python.org/downloads/
    echo При установке ОБЯЗАТЕЛЬНО отметьте "Add Python to PATH",
    echo затем запустите install.bat снова.
    echo.
    pause
    exit /b 1
)

echo [1/4] Python обнаружен:
python --version
echo.

if exist ".venv\Scripts\python.exe" (
    echo [2/4] Окружение .venv уже создано - пропускаю.
) else (
    echo [2/4] Создаю виртуальное окружение .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось создать .venv.
        pause
        exit /b 1
    )
)
echo.

echo [3/4] Устанавливаю зависимости (несколько минут) ...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить зависимости. Проверьте интернет.
    pause
    exit /b 1
)
echo.

echo [4/4] Скачиваю модель распознавания large-v3-turbo (~1.5 ГБ, разово) ...
".venv\Scripts\python.exe" -c "from faster_whisper import WhisperModel; WhisperModel('large-v3-turbo', device='cpu', compute_type='int8'); print('Модель готова.')"
if errorlevel 1 (
    echo [!] Модель не докачалась - не страшно, она скачается при первом запуске.
)
echo.

echo ============================================
echo    Готово. Запуск: двойной клик по start.bat
echo ============================================
echo.
pause
