#!/usr/bin/env bash
# VoiceKey bootstrap для macOS.
# Запуск одной командой в Terminal:
#   curl -fsSL https://raw.githubusercontent.com/serenkiy-commits/voicekey/main/bootstrap.sh | bash
set -e
REPO_GIT="https://github.com/serenkiy-commits/voicekey.git"
REPO_ZIP="https://github.com/serenkiy-commits/voicekey/archive/refs/heads/main.zip"
DIR="$HOME/voicekey"

echo "=== VoiceKey bootstrap (macOS) ==="

# 1. Python с поддержкой Tk
if ! command -v python3 >/dev/null 2>&1; then
    if command -v brew >/dev/null 2>&1; then
        echo "Python не найден, ставлю через Homebrew..."
        brew install python python-tk
    else
        echo "python3 не найден. Установи Python с https://www.python.org/downloads/macos/ (Tk внутри)"
        echo "и запусти эту команду снова."
        exit 1
    fi
fi
echo "Python: $(python3 --version)"

# 2. Получить проект
if [ -d "$DIR/.git" ]; then
    echo "Папка voicekey уже есть, обновляю..."
    git -C "$DIR" pull --ff-only
elif [ -d "$DIR" ]; then
    echo "Папка $DIR уже существует, использую её."
elif command -v git >/dev/null 2>&1; then
    git clone "$REPO_GIT" "$DIR"
else
    echo "Скачиваю архив проекта..."
    TMP="$(mktemp -d)"
    curl -fsSL "$REPO_ZIP" -o "$TMP/voicekey.zip"
    unzip -q "$TMP/voicekey.zip" -d "$TMP"
    mv "$TMP/voicekey-main" "$DIR"
    rm -rf "$TMP"
fi

# 3. Установка (venv + зависимости + модель)
echo "Запускаю install.sh..."
bash "$DIR/install.sh"

# 4. Сделать лаунчер исполняемым
chmod +x "$DIR/start.command" 2>/dev/null || true

echo "Готово. Запуск: ./start.command в папке $DIR"
echo "Не забудь права macOS (Accessibility / Input Monitoring / Microphone) и CapsLock = No Action — см. INSTALL.md, раздел 3."
