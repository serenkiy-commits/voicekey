import json
import os
import sys
import threading
import time
import traceback
import ctypes

import customtkinter as ctk

from voicekey.transcriber import Transcriber
from voicekey.recorder import Recorder
from voicekey.hotkey import CapsLockHook
from voicekey.inserter import insert_text
from voicekey.postprocess import postprocess, load_dictionary
from voicekey.history import save_transcription
from voicekey.ui.tray import TrayApp
from voicekey.ui.history_window import HistoryWindow
from voicekey.ui.settings import SettingsWindow
from voicekey.ui.overlay import RecordingOverlay

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
LOG_PATH = os.path.join(os.path.dirname(__file__), "voicekey.log")


def log(msg):
    """Печать в консоль + дозапись в voicekey.log (нужно для диагностики под pythonw)."""
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def beep(freq, duration_ms):
    """Звуковой сигнал. Windows: winsound.Beep; macOS/Linux: тон через sounddevice."""
    if sys.platform == "win32":
        import winsound
        winsound.Beep(int(freq), int(duration_ms))
        return
    try:
        import numpy as np
        import sounddevice as sd
        sr = 44100
        n = int(sr * duration_ms / 1000)
        t = np.linspace(0, duration_ms / 1000, n, False)
        tone = (np.sin(2 * np.pi * freq * t) * 0.2).astype(np.float32)
        sd.play(tone, sr, blocking=True)
    except Exception:
        pass


def get_active_window_title():
    if sys.platform != "win32":
        return ""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    except Exception:
        return ""


class VoiceKey:
    def __init__(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.transcriber = Transcriber(
            model_size=self.config["model_size"],
            device=self.config["device"],
            compute_type=self.config["compute_type"],
        )
        self.recorder = Recorder(
            device=self.config.get("microphone"),
        )
        self.dictionary = load_dictionary()
        self.recording = False
        self._record_start_time = 0

        self.history_window = HistoryWindow()
        self.settings_window = SettingsWindow(on_config_changed=self._on_config_changed)

        self.tray = TrayApp(
            on_show_history=self._show_history,
            on_show_settings=self._show_settings,
            on_quit=self._quit,
        )

        self.hook = CapsLockHook(
            on_toggle=self._on_toggle,
            double_press_threshold_ms=self.config.get("double_press_threshold_ms", 300),
        )

        self._ctk_root = None
        self.overlay = None

    def run(self):
        log("[VoiceKey] Loading model...")
        self.transcriber.load_model()
        log(f"[VoiceKey] Model ready on device={self.transcriber.device}. CapsLock = toggle recording.")

        # Start hotkey listener
        self.hook.start()

        # Init CTk root (hidden, for toplevel windows)
        self._ctk_root = ctk.CTk()
        self._ctk_root.withdraw()

        # Init overlay
        self.overlay = RecordingOverlay(self._ctk_root)

        # Run tray icon. macOS (Cocoa) требует GUI в главном потоке —
        # используем run_detached; Windows/Linux работают из фонового потока.
        icon = self.tray.create()
        if sys.platform == "darwin":
            icon.run_detached()
        else:
            tray_thread = threading.Thread(target=icon.run, daemon=True)
            tray_thread.start()

        # Beep to signal ready
        beep(800, 150)

        # Main loop for tkinter
        self._ctk_root.mainloop()

    def _on_toggle(self):
        if not self.recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        self.recording = True
        self._record_start_time = time.time()
        self.tray.set_recording()
        # Show overlay animation at cursor
        if self._ctk_root and self.overlay:
            self._ctk_root.after(0, lambda: self.overlay.show("recording"))
        # Beep: start
        beep(600, 100)
        self.recorder.start()
        log("[VoiceKey] Recording started.")

    def _stop_recording(self):
        self.recording = False
        duration = time.time() - self._record_start_time
        # Beep: stop (double)
        beep(800, 80)
        beep(1000, 80)
        log("[VoiceKey] Recording stopped. Transcribing...")

        self.tray.set_processing()
        # Switch overlay to processing animation
        if self._ctk_root and self.overlay:
            self._ctk_root.after(0, lambda: self.overlay.set_processing())
        audio = self.recorder.stop()

        if audio is None or len(audio) < 1600:  # <0.1s
            log("[VoiceKey] Аудио пустое/слишком короткое — пропуск. Проверьте микрофон.")
            if self._ctk_root and self.overlay:
                self._ctk_root.after(0, self.overlay.hide)
            self.tray.set_idle()
            return

        try:
            import numpy as np
            rms = float(np.sqrt(np.mean(audio.astype("float64") ** 2)))
        except Exception:
            rms = -1.0
        log(f"[VoiceKey] Аудио: {len(audio)} сэмплов, rms={rms:.5f}")

        # Transcribe
        app_name = get_active_window_title()
        try:
            raw_text = self.transcriber.transcribe(audio)
            text = postprocess(raw_text, self.dictionary)
        except Exception:
            log("[VoiceKey] Ошибка распознавания:\n" + traceback.format_exc())
            if self.overlay:
                self.overlay.hide_immediate()
            self.tray.set_idle()
            return

        # Hide overlay immediately before inserting text
        if self.overlay:
            self.overlay.hide_immediate()
        time.sleep(0.2)

        if text:
            log(f"[VoiceKey] Результат: {text!r}")
            try:
                insert_text(text)
            except Exception:
                log("[VoiceKey] Ошибка вставки (буфер/клавиши):\n" + traceback.format_exc())
            save_transcription(text, duration_sec=duration, app_name=app_name)
        else:
            log(f"[VoiceKey] Пустое распознавание (raw={raw_text!r}). Вероятно тишина в записи — проверьте микрофон/громкость/язык.")

        self.tray.set_idle()

    def _show_history(self):
        if self._ctk_root:
            self._ctk_root.after(0, self.history_window.show)

    def _show_settings(self):
        if self._ctk_root:
            self._ctk_root.after(0, self.settings_window.show)

    def _on_config_changed(self, new_config):
        self.config = new_config
        self.dictionary = load_dictionary()
        print(f"[VoiceKey] Config updated.")

    def _quit(self):
        if self._ctk_root:
            self._ctk_root.after(0, self._ctk_root.destroy)


def main():
    app = VoiceKey()
    app.run()


if __name__ == "__main__":
    main()
