import sys
import time
import pyperclip


if sys.platform == "win32":
    import pyautogui

    def _paste():
        pyautogui.hotkey("ctrl", "v")

else:
    from pynput.keyboard import Controller, Key

    _kbd = Controller()

    def _paste():
        with _kbd.pressed(Key.cmd):
            _kbd.press("v")
            _kbd.release("v")


def insert_text(text):
    if not text:
        return
    pyperclip.copy(text)
    time.sleep(0.1)
    _paste()
