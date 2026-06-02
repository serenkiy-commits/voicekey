# VoiceKey — установка с нуля

Локальный голосовой ввод. Нажал **CapsLock** → говоришь → ещё раз CapsLock → текст
распознаётся офлайн (Whisper) и вставляется в активное окно. Работает на **Windows** и **macOS**.

Иконка в трее, история (SQLite), настройки, словарь автозамен.

Эта инструкция написана так, чтобы человек **с чистой системы** смог развернуть программу:
каждая команда и ссылка прописаны явно.

---

## 0. Что понадобится (одинаково для Windows и macOS)

- **Python 3.10–3.12** — на 3.13+ часть пакетов может ещё не собираться. Ссылки ниже.
- **Git** — чтобы скачать проект командой `git clone`. Ссылки ниже.
- **Микрофон.**
- **~2–3 ГБ свободного места** под модель распознавания.
- **Интернет при первой установке** — Python, библиотеки и модель качаются из сети.
  После установки программа работает офлайн.
- **GPU NVIDIA — необязательно.** Без видеокарты всё работает на процессоре (медленнее).

> Проект опубликован здесь: `https://github.com/serenkiy-commits/voicekey`. Команды
> `git clone` ниже используют этот адрес. (Разворачиваете свою копию: см. раздел 8.)

---

## 1. Windows — быстрый путь (рекомендуется)

### 1.1 Установить Python

1. Откройте <https://www.python.org/downloads/> и скачайте **Python 3.12** (кнопка
   «Download Python 3.12.x»).
2. Запустите установщик. **ОБЯЗАТЕЛЬНО** поставьте галочку **«Add python.exe to PATH»**
   внизу первого окна, затем «Install Now».
3. Проверьте — откройте **PowerShell** (Win → наберите `powershell` → Enter) и выполните:

   ```powershell
   python --version
   ```

   Должно вывести `Python 3.12.x`. Если пишет, что команда не найдена — переустановите
   Python с галочкой PATH.

### 1.2 Установить Git

1. Скачайте установщик: <https://git-scm.com/download/win> (скачается автоматически).
2. Установите со всеми настройками по умолчанию (просто жмите «Next»).
3. Проверка:

   ```powershell
   git --version
   ```

### 1.3 Скачать проект

В PowerShell перейдите в папку, куда хотите положить программу (например, рабочий стол),
и клонируйте репозиторий:

```powershell
cd $env:USERPROFILE\Desktop
git clone https://github.com/serenkiy-commits/voicekey.git
cd voicekey
```

Появится папка `voicekey`. Дальше все команды — **внутри неё**.

### 1.4 Установить (один двойной клик)

В Проводнике откройте папку `voicekey` и **дважды кликните `install.bat`**.

Скрипт сам:
1. проверит Python,
2. создаст изолированное окружение `.venv`,
3. поставит все библиотеки,
4. скачает модель распознавания **large-v3-turbo** (~1.5 ГБ, разово).

Дождитесь строки `Готово` и нажмите любую клавишу.

### 1.5 Запуск

Дважды кликните **`start.bat`**.

При старте прозвучит короткий сигнал, в трее (правый нижний угол) появится зелёный
кружок — программа готова. Нажмите **CapsLock**, говорите, ещё раз CapsLock — текст
вставится в активное поле.

---

## 2. Windows — ручной путь (без скриптов)

Если хотите выполнить всё руками (или `install.bat` не сработал). PowerShell в папке
`voicekey`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

> Если PowerShell ругается «выполнение скриптов отключено», один раз выполните
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, подтвердите `Y`, затем снова
> активируйте окружение командой `.\.venv\Scripts\Activate.ps1`.

Скачать модель заранее (необязательно — иначе скачается при первом запуске):

```powershell
python -c "from faster_whisper import WhisperModel; WhisperModel('large-v3-turbo', device='cpu', compute_type='int8')"
```

Запуск (из активированного окружения):

```powershell
cd ..
python -m voicekey.main
```

> Важно: запускать `python -m voicekey.main` нужно из **родительской** папки (на уровень
> выше `voicekey`). Скрипт `start.bat` делает этот переход сам.

### 2.1 Видеокарта NVIDIA (ускорение, необязательно)

По умолчанию в `config.json` стоит `"device": "cuda"`. Если рабочих библиотек CUDA нет,
программа **сама переключится на процессор** — ничего не сломается, просто будет медленнее.

Чтобы реально задействовать GPU, нужны свежий драйвер NVIDIA и runtime-библиотеки CUDA 12
+ cuDNN 9. Самый простой способ — поставить их прямо в окружение (PowerShell в папке
`voicekey`, окружение активировано):

```powershell
pip install nvidia-cublas-cu12 nvidia-cudnn-cu12==9.*
```

После этого `config.json` оставьте как есть:

```json
"device": "cuda",
"compute_type": "float16"
```

Если хотите принудительно CPU — поставьте:

```json
"device": "cpu",
"compute_type": "int8"
```

### 2.2 Автозапуск при входе в Windows (необязательно)

PowerShell в папке `voicekey`, окружение активировано:

```powershell
python -m voicekey.autostart          # включить
python -m voicekey.autostart remove   # выключить
```

Добавляет запись в реестр `HKCU\...\Run`.

---

## 3. macOS

> **Честно:** проект разрабатывался и тестировался на Windows. macOS-ветки кода написаны
> по документации (pynput, launchd, sounddevice), но на «живом» Mac автором не прогонялись.
> Базовый сценарий (CapsLock → запись → вставка) должен работать; возможна доводка
> трея/оверлея — см. раздел 6.

### 3.1 Установить Python с поддержкой Tk

Системного Python мало — нужен Tkinter. Вариант проще:

1. Откройте <https://www.python.org/downloads/macos/>, скачайте установщик
   **Python 3.12** (.pkg), установите. Tk уже внутри.
2. Проверка в Terminal:

   ```bash
   python3 --version
   python3 -m tkinter      # должно открыться маленькое тестовое окно
   ```

Альтернатива через Homebrew: `brew install python python-tk`.

### 3.2 Установить Git

Обычно Git ставится вместе с инструментами разработчика:

```bash
xcode-select --install
```

Либо скачайте с <https://git-scm.com/download/mac>. Проверка: `git --version`.

### 3.3 Скачать проект

В Terminal:

```bash
cd ~/Desktop
git clone https://github.com/serenkiy-commits/voicekey.git
cd voicekey
```

### 3.4 Установить

```bash
bash install.sh
```

Скрипт создаст `.venv`, поставит библиотеки (на macOS вместо `keyboard` ставится
**pynput** автоматически) и скачает модель.

> Если трей-иконка потом не появится, доустановите:
> `pip install pyobjc-framework-Cocoa pyobjc-framework-Quartz`
> (предварительно активировав окружение: `source .venv/bin/activate`).

Ручной путь — то же самое командами:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.5 Разрешения macOS (без них не работает)

**System Settings → Privacy & Security:**

1. **Accessibility** — добавьте Terminal и включите (без этого pynput не ловит клавиши и
   не вставляет текст).
2. **Input Monitoring** — там же добавьте Terminal.
3. **Microphone** — разрешите доступ.

После выдачи прав перезапустите программу.

### 3.6 Отключить штатное действие CapsLock

Чтобы CapsLock работал как кнопка диктовки, а не переключал регистр:

**System Settings → Keyboard → Keyboard Shortcuts… → Modifier Keys** → для **Caps Lock**
выберите **No Action (Без действия)**.

### 3.7 Запуск

```bash
chmod +x start.command        # один раз, чтобы файл стал исполняемым
./start.command
```

Либо вручную из активированного окружения:

```bash
cd ..
python3 -m voicekey.main
```

CUDA на Mac нет — программа автоматически работает на CPU (`int8`). Для скорости можно
поставить модель полегче (см. раздел 5).

### 3.8 Автозапуск при входе (необязательно)

```bash
python3 -m voicekey.autostart          # создаст LaunchAgent .plist
python3 -m voicekey.autostart remove   # удалит
launchctl load ~/Library/LaunchAgents/com.voicekey.agent.plist   # активировать сразу
```

---

## 4. Где что лежит и какие ссылки нужны

| Что | Откуда брать |
|---|---|
| Python (Windows) | <https://www.python.org/downloads/> |
| Python (macOS) | <https://www.python.org/downloads/macos/> |
| Git (Windows) | <https://git-scm.com/download/win> |
| Git (macOS) | `xcode-select --install` или <https://git-scm.com/download/mac> |
| Сам проект | `git clone https://github.com/serenkiy-commits/voicekey.git` |
| Модель large-v3-turbo | <https://huggingface.co/mobiuslabsgmbh/faster-whisper-large-v3-turbo> |
| GPU-библиотеки (Windows) | `pip install nvidia-cublas-cu12 nvidia-cudnn-cu12==9.*` |

---

## 5. Модель распознавания

В `config.json` по умолчанию указано `"model_size": "large-v3-turbo"`. При первой
установке `install.bat` / `install.sh` скачивают её автоматически (репозиторий
<https://huggingface.co/mobiuslabsgmbh/faster-whisper-large-v3-turbo>, ~1.5 ГБ) и кешируют.
Дальше интернет не нужен.

**Другие модели.** Лёгкие модели качаются автоматически при выборе — можно переключать в
окне «Настройки» или в `config.json`:

```json
"model_size": "small"
```

Доступно: `tiny`, `base`, `small`, `medium`, `large-v3`, `large-v3-turbo`. Чем легче —
тем быстрее и менее точно. На слабом ПК/без GPU начните с `small` или `medium`.

**Полностью офлайн (скачать модель папкой заранее).** Из папки `voicekey`, окружение
активировано:

```powershell
pip install huggingface_hub
hf download mobiuslabsgmbh/faster-whisper-large-v3-turbo --local-dir models-large-v3-turbo
```

Затем в `config.json`:

```json
"model_size": "models-large-v3-turbo"
```

Программа увидит локальную папку рядом с собой и не полезет в интернет. (Папки `models-*`
исключены из git, репозиторий они не раздувают.)

---

## 6. Как пользоваться

1. **CapsLock** — начать запись (красный кружок в трее, точки у курсора).
2. Говорите.
3. **CapsLock** ещё раз — остановить. Текст распознаётся (жёлтый кружок) и вставляется
   в активное поле.
4. **Трей → История** — все распознавания (хранятся в `history.db`).
5. **Трей → Настройки** — модель, порог двойного нажатия, словарь автозамен.
6. **Трей → Выход** — закрыть.

**Словарь автозамен** (`dictionary.json` или окно настроек) — формат `слово = замена`,
по одной паре на строку. Применяется к каждому распознаванию.

Язык распознавания — русский (зашит в `transcriber.py`).

---

## 7. Если что-то не работает

| Симптом | Что проверить |
|---|---|
| `python` / `git` «не является командой» | Python ставили без галочки **Add to PATH**, либо не перезапустили PowerShell. Переустановите Python с галочкой, откройте PowerShell заново. |
| `ModuleNotFoundError: voicekey` | Запускаете не из той папки. Нужно быть в **родителе** папки `voicekey`. Проще — запускать через `start.bat` / `start.command`. |
| `install.bat` мигнул и закрылся | Запустите его из PowerShell, чтобы увидеть ошибку: `cd voicekey` затем `.\install.bat`. |
| Не реагирует на CapsLock (Windows) | Запустите `start.bat` **от имени администратора** — библиотека `keyboard` требует прав на перехват. |
| Не реагирует на CapsLock (macOS) | Не выданы **Accessibility / Input Monitoring**, либо не отключено действие CapsLock (разделы 3.5–3.6). |
| Распознаёт очень медленно | Это CPU. Возьмите модель полегче (`small`/`medium`) или включите GPU (раздел 2.1). |
| CUDA-ошибки в консоли (Windows) | Не критично — программа сама уйдёт на CPU. Для GPU обновите драйвер NVIDIA и выполните `pip install nvidia-cublas-cu12 nvidia-cudnn-cu12==9.*`. |
| `tkinter` не найден (macOS) | Поставьте Python с Tk: `brew install python-tk` или сборку с python.org. |
| Трей-иконки нет (macOS) | `pip install pyobjc-framework-Cocoa pyobjc-framework-Quartz`. |
| Микрофон не тот | В `config.json` поле `microphone` — индекс устройства (число). `null` = системный по умолчанию. |

---

## 8. Для того, кто публикует проект (один раз)

Если репозитория ещё нет, превратите папку `voicekey` в репозиторий и выложите на GitHub.
PowerShell в папке `voicekey`:

```powershell
git init
git add .
git commit -m "VoiceKey: первая версия"
```

Создайте пустой репозиторий на GitHub (через сайт или `gh repo create`), затем:

```powershell
git remote add origin https://github.com/<ВАШ_АККАУНТ>/voicekey.git
git branch -M main
git push -u origin main
```

Файл `.gitignore` уже исключает `.venv/`, `__pycache__/`, модель `models-*/` и `history.db`,
поэтому в репозиторий попадёт только код. Пользователям давайте адрес
`https://github.com/<ВАШ_АККАУНТ>/voicekey.git` для команды `git clone` из раздела 1.3 / 3.3.

---

## 9. Удаление

1. Выключите автозапуск: `python -m voicekey.autostart remove` (Windows) /
   `python3 -m voicekey.autostart remove` (macOS).
2. Удалите папку `voicekey`.
3. (macOS) Удалите `~/Library/LaunchAgents/com.voicekey.agent.plist`, если остался.
4. Кеш скачанных моделей: `%USERPROFILE%\.cache\huggingface` (Windows) /
   `~/.cache/huggingface` (macOS) — удалите при желании.
