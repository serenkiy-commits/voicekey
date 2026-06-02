import sys
import threading
import time


if sys.platform == "win32":
    import keyboard

    class CapsLockHook:
        def __init__(self, on_toggle, double_press_threshold_ms=300):
            self.on_toggle = on_toggle
            self.threshold = double_press_threshold_ms / 1000.0
            self._last_press_time = 0
            self._suppressed = True

        def start(self):
            keyboard.hook_key(
                "caps lock",
                callback=self._on_capslock,
                suppress=True,
            )
            print("[Hotkey] CapsLock hook installed via keyboard library.")

        def _on_capslock(self, event):
            if event.event_type != keyboard.KEY_DOWN:
                return

            now = time.time()
            delta = now - self._last_press_time
            self._last_press_time = now

            if delta < self.threshold:
                # Double press — simulate real CapsLock
                print("[Hotkey] Double press — CapsLock passthrough")
                keyboard.send("caps lock", do_press=True, do_release=True)
                return

            # Single press — toggle recording
            print("[Hotkey] CapsLock toggle!")
            threading.Thread(target=self.on_toggle, daemon=True).start()

else:
    # macOS / Linux: библиотека keyboard ненадёжна (требует root, suppress
    # не работает). Используем pynput. Подавления нет — пользователь должен
    # отключить действие CapsLock в системе (см. INSTALL.md), чтобы клавиша
    # работала как чистый триггер, а не переключала регистр.
    from pynput import keyboard as pk

    class CapsLockHook:
        def __init__(self, on_toggle, double_press_threshold_ms=300):
            self.on_toggle = on_toggle
            self._listener = None

        def start(self):
            self._listener = pk.Listener(on_press=self._on_press)
            self._listener.start()
            print("[Hotkey] CapsLock listener installed via pynput.")

        def _on_press(self, key):
            if key == pk.Key.caps_lock:
                print("[Hotkey] CapsLock toggle!")
                threading.Thread(target=self.on_toggle, daemon=True).start()
