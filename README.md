# VoiceKey

Локальный голосовой ввод для **Windows** и **macOS**. Нажми **CapsLock**, говори, ещё раз
CapsLock — текст распознаётся офлайн (faster-whisper) и вставляется в активное окно.
Иконка в трее, история, настройки, словарь автозамен.

## Установка одной командой

**Windows** (PowerShell):

```powershell
irm https://raw.githubusercontent.com/serenkiy-commits/voicekey/main/bootstrap.ps1 | iex
```

**macOS** (Terminal):

```bash
curl -fsSL https://raw.githubusercontent.com/serenkiy-commits/voicekey/main/bootstrap.sh | bash
```

Скрипт проверит/поставит Python, скачает проект и зависимости, скачает модель и подготовит
запуск. После установки на Windows запуск через `start.bat`, на macOS через `./start.command`.

## Через pipx / uv (если Python уже установлен)

Аналог `npx` для Python. Установить как команду:

```bash
pipx install git+https://github.com/serenkiy-commits/voicekey.git
voicekey
```

Или запустить разово без установки:

```bash
uvx --from git+https://github.com/serenkiy-commits/voicekey.git voicekey
```

> Данные (config.json, история) хранятся внутри окружения пакета. Для постоянного
> использования предпочтительнее `pipx install` (или `uv tool install`), а не разовый `uvx`.

## Вручную (clone)

Полная пошаговая инструкция: **[INSTALL.md](INSTALL.md)** (есть и оформленная
[INSTALL.html](INSTALL.html) для пересылки клиентам).

```bash
git clone https://github.com/serenkiy-commits/voicekey.git
cd voicekey
# Windows: дважды кликнуть install.bat, затем start.bat
# macOS:   bash install.sh, затем ./start.command
```

## Как пользоваться

**CapsLock** — старт записи, **CapsLock** — стоп и вставка. Трей: История / Настройки /
Выход. Словарь автозамен — `dictionary.json` (формат `слово = замена`). Язык распознавания
русский. Модель по умолчанию `large-v3-turbo`, переключается в настройках.

## Требования

Python 3.10–3.12, микрофон, ~2–3 ГБ под модель. GPU NVIDIA необязателен (без него работает
на CPU). Подробности и решение проблем — в [INSTALL.md](INSTALL.md).
