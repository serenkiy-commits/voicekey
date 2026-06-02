import sys
import tkinter as tk

IS_WIN = sys.platform == "win32"

if IS_WIN:
    import ctypes
    import ctypes.wintypes

    def _win_caret_position():
        """Get the text cursor (caret) position using Windows API."""
        user32 = ctypes.windll.user32

        # Try to get caret position from the foreground window's thread
        foreground = user32.GetForegroundWindow()
        thread_id = user32.GetWindowThreadProcessId(foreground, None)
        current_thread = ctypes.windll.kernel32.GetCurrentThreadId()

        point = ctypes.wintypes.POINT()

        # Attach to the target thread to access its caret
        attached = user32.AttachThreadInput(current_thread, thread_id, True)
        if attached:
            user32.GetCaretPos(ctypes.byref(point))
            # Convert from client coords to screen coords
            user32.ClientToScreen(foreground, ctypes.byref(point))
            user32.AttachThreadInput(current_thread, thread_id, False)
            if point.x != 0 or point.y != 0:
                return point.x, point.y

        # Fallback: use mouse cursor position
        user32.GetCursorPos(ctypes.byref(point))
        return point.x, point.y


class RecordingOverlay:
    """Floating animated overlay shown near the text cursor during recording."""

    def __init__(self, root):
        self._root = root
        self._win = None
        self._canvas = None
        self._anim_id = None
        self._frame = 0
        self._mode = "recording"  # "recording" or "processing"
        self._saved_hwnd = None  # foreground window before overlay (Windows only)

    def _caret_xy(self):
        if IS_WIN:
            return _win_caret_position()
        # macOS/Linux: точной позиции каретки нет — берём позицию указателя мыши
        try:
            return self._root.winfo_pointerxy()
        except Exception:
            return 100, 100

    def show(self, mode="recording"):
        self._mode = mode
        self._frame = 0

        # Remember which window had focus before overlay (Windows only)
        if IS_WIN:
            self._saved_hwnd = ctypes.windll.user32.GetForegroundWindow()

        x, y = self._caret_xy()

        if self._win is not None:
            self._update_mode(mode)
            self._win.geometry(f"+{x + 8}+{y + 4}")
            self._win.deiconify()
            return

        self._win = tk.Toplevel(self._root)
        self._win.overrideredirect(True)
        self._win.attributes("-topmost", True)
        self._win.attributes("-alpha", 0.9)
        self._win.config(bg="black")

        if IS_WIN:
            # Make black transparent (Windows-only Tk option)
            self._win.wm_attributes("-transparentcolor", "black")

            # Make window non-focusable so it doesn't steal focus from target app
            self._win.update_idletasks()
            hwnd = int(self._win.frame(), 16) if hasattr(self._win, 'frame') else self._win.winfo_id()
            WS_EX_NOACTIVATE = 0x08000000
            WS_EX_TOOLWINDOW = 0x00000080
            GWL_EXSTYLE = -20
            user32 = ctypes.windll.user32
            style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW)

        self._canvas = tk.Canvas(
            self._win, width=60, height=24, bg="black", highlightthickness=0
        )
        self._canvas.pack()

        self._win.geometry(f"60x24+{x + 8}+{y + 4}")
        self._animate()

    def _update_mode(self, mode):
        self._mode = mode
        self._frame = 0

    def set_processing(self):
        if self._win:
            self._mode = "processing"
            self._frame = 0
            x, y = self._caret_xy()
            self._win.geometry(f"+{x + 8}+{y + 4}")

    def hide(self):
        if self._anim_id:
            self._root.after_cancel(self._anim_id)
            self._anim_id = None
        if self._win:
            self._win.withdraw()

    def hide_immediate(self):
        """Hide the overlay. On Windows uses Win32 directly (safe from any thread)
        and restores focus to the window that was active before overlay."""
        if not self._win:
            return
        if IS_WIN:
            try:
                hwnd = int(self._win.frame(), 16) if hasattr(self._win, 'frame') else self._win.winfo_id()
                SW_HIDE = 0
                ctypes.windll.user32.ShowWindow(hwnd, SW_HIDE)
            except Exception:
                pass
            # Restore focus to original window
            if self._saved_hwnd:
                try:
                    ctypes.windll.user32.SetForegroundWindow(self._saved_hwnd)
                except Exception:
                    pass
        # Schedule proper tkinter cleanup
        self._root.after(0, self.hide)

    def _animate(self):
        if not self._canvas or not self._win:
            return

        self._canvas.delete("all")

        if self._mode == "recording":
            self._draw_recording_dots()
        else:
            self._draw_processing_spinner()

        self._frame += 1
        self._anim_id = self._root.after(120, self._animate)

    def _draw_recording_dots(self):
        """Three pulsing red dots — voice recording indicator."""
        num_dots = 3
        phase = self._frame % 12

        for i in range(num_dots):
            cx = 14 + i * 16
            cy = 12

            # Each dot pulses in sequence
            dot_phase = (phase - i * 2) % 12
            if dot_phase < 4:
                radius = 3 + dot_phase
                alpha_factor = 0.6 + dot_phase * 0.1
            elif dot_phase < 8:
                radius = 7 - (dot_phase - 4)
                alpha_factor = 1.0 - (dot_phase - 4) * 0.1
            else:
                radius = 3
                alpha_factor = 0.6

            # Red color with varying brightness
            r = int(min(255, 200 * alpha_factor + 55))
            g = int(40 * alpha_factor)
            b = int(40 * alpha_factor)
            color = f"#{r:02x}{g:02x}{b:02x}"

            self._canvas.create_oval(
                cx - radius, cy - radius, cx + radius, cy + radius, fill=color, outline=""
            )

    def _draw_processing_spinner(self):
        """Rotating yellow dots — processing/transcription indicator."""
        import math

        num_dots = 4
        cx, cy = 30, 12
        radius = 8

        for i in range(num_dots):
            angle = (self._frame * 0.5 + i * (math.pi * 2 / num_dots))
            dx = cx + math.cos(angle) * radius
            dy = cy + math.sin(angle) * radius

            # Fade based on position in sequence
            brightness = 1.0 - (i / num_dots) * 0.6
            r = int(220 * brightness)
            g = int(200 * brightness)
            b = int(30 * brightness)
            color = f"#{r:02x}{g:02x}{b:02x}"

            dot_r = 3 - i * 0.4
            self._canvas.create_oval(
                dx - dot_r, dy - dot_r, dx + dot_r, dy + dot_r, fill=color, outline=""
            )

    def destroy(self):
        self.hide()
        if self._win:
            self._win.destroy()
            self._win = None
