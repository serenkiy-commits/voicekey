"""Add/remove VoiceKey from startup (Windows registry / macOS LaunchAgent)."""
import os
import sys

APP_NAME = "VoiceKey"
# Родитель папки voicekey — рабочая директория для запуска `python -m voicekey.main`
VOICEKEY_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


if sys.platform == "win32":
    import winreg

    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    # Запуск через venv, если он есть (иначе системный pythonw)
    _PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
    _VENV_PYTHONW = os.path.join(_PACKAGE_DIR, ".venv", "Scripts", "pythonw.exe")
    _PYTHONW = _VENV_PYTHONW if os.path.exists(_VENV_PYTHONW) else "pythonw"
    COMMAND = f'"{_PYTHONW}" -m voicekey.main'

    def add_to_startup():
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        # cmd /c для рабочей директории (родитель пакета); пути в кавычках на случай пробелов
        value = f'cmd /c "cd /d "{VOICEKEY_DIR}" && {COMMAND}"'
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, value)
        winreg.CloseKey(key)
        print("VoiceKey added to startup.")

    def remove_from_startup():
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, APP_NAME)
            winreg.CloseKey(key)
            print("VoiceKey removed from startup.")
        except FileNotFoundError:
            print("VoiceKey was not in startup.")

else:
    # macOS: LaunchAgent plist в ~/Library/LaunchAgents
    PLIST_LABEL = "com.voicekey.agent"
    PLIST_PATH = os.path.expanduser(f"~/Library/LaunchAgents/{PLIST_LABEL}.plist")

    def add_to_startup():
        python = sys.executable
        plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python}</string>
        <string>-m</string>
        <string>voicekey.main</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{VOICEKEY_DIR}</string>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
        os.makedirs(os.path.dirname(PLIST_PATH), exist_ok=True)
        with open(PLIST_PATH, "w") as f:
            f.write(plist)
        print(f"VoiceKey LaunchAgent written to {PLIST_PATH}")
        print(f"Активируйте сейчас: launchctl load {PLIST_PATH}")

    def remove_from_startup():
        if os.path.exists(PLIST_PATH):
            os.system(f"launchctl unload {PLIST_PATH} 2>/dev/null")
            os.remove(PLIST_PATH)
            print("VoiceKey LaunchAgent removed.")
        else:
            print("VoiceKey was not in startup.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "remove":
        remove_from_startup()
    else:
        add_to_startup()
