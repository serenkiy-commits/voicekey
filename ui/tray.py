import pystray
from PIL import Image, ImageDraw


def _create_icon(color):
    img = Image.new("RGB", (64, 64), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    draw.ellipse([12, 12, 52, 52], fill=color)
    return img


ICON_IDLE = _create_icon((0, 200, 0))
ICON_RECORDING = _create_icon((220, 30, 30))
ICON_PROCESSING = _create_icon((220, 200, 0))


class TrayApp:
    def __init__(self, on_show_history, on_show_settings, on_quit):
        self.on_show_history = on_show_history
        self.on_show_settings = on_show_settings
        self.on_quit = on_quit
        self._icon = None

    def create(self):
        menu = pystray.Menu(
            pystray.MenuItem("VoiceKey", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("История", lambda: self.on_show_history()),
            pystray.MenuItem("Настройки", lambda: self.on_show_settings()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Выход", lambda: self.on_quit()),
        )
        self._icon = pystray.Icon("voicekey", ICON_IDLE, "VoiceKey — Idle", menu)
        return self._icon

    def set_idle(self):
        if self._icon:
            self._icon.icon = ICON_IDLE
            self._icon.title = "VoiceKey — Idle"

    def set_recording(self):
        if self._icon:
            self._icon.icon = ICON_RECORDING
            self._icon.title = "VoiceKey — Recording..."

    def set_processing(self):
        if self._icon:
            self._icon.icon = ICON_PROCESSING
            self._icon.title = "VoiceKey — Transcribing..."
