#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "============================================"
echo "   VoiceKey - установка (macOS / Linux)"
echo "============================================"
echo

if ! command -v python3 >/dev/null 2>&1; then
    echo "[ОШИБКА] python3 не найден."
    echo "Установите Python 3.11 или 3.12 с поддержкой Tk:"
    echo "  - https://www.python.org/downloads/macos/  (рекомендуется, Tk внутри)"
    echo "  - либо: brew install python python-tk"
    exit 1
fi

echo "[1/4] Python обнаружен:"
python3 --version
echo

if [ -d ".venv" ]; then
    echo "[2/4] Окружение .venv уже создано - пропускаю."
else
    echo "[2/4] Создаю виртуальное окружение .venv ..."
    python3 -m venv .venv
fi
echo

echo "[3/4] Устанавливаю зависимости (несколько минут) ..."
.venv/bin/python -m pip install --upgrade pip || true
.venv/bin/python -m pip install -r requirements.txt
echo

echo "[4/4] Скачиваю модель распознавания large-v3-turbo (~1.5 ГБ, разово) ..."
.venv/bin/python -c "from faster_whisper import WhisperModel; WhisperModel('large-v3-turbo', device='cpu', compute_type='int8'); print('Модель готова.')" || echo "[!] Модель не докачалась - скачается при первом запуске."
echo

echo "============================================"
echo "   Готово. Не забудьте права macOS (Accessibility / Input Monitoring /"
echo "   Microphone) и CapsLock = No Action. Подробности в INSTALL.md, раздел 3."
echo "   Запуск: ./start.command"
echo "============================================"
