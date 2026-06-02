#!/usr/bin/env bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR/.."
if [ ! -x "$DIR/.venv/bin/python" ]; then
    echo "Окружение .venv не найдено. Сначала запустите: bash \"$DIR/install.sh\""
    read -n 1 -s -r -p "Нажмите любую клавишу для выхода..."
    exit 1
fi
exec "$DIR/.venv/bin/python" -m voicekey.main
