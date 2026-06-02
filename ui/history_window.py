import customtkinter as ctk
import pyperclip
from voicekey.history import get_history


class HistoryWindow:
    def __init__(self):
        self._win = None

    def show(self):
        if self._win and self._win.winfo_exists():
            self._win.focus()
            return

        self._win = ctk.CTkToplevel()
        self._win.title("VoiceKey — История")
        self._win.geometry("700x500")
        self._win.attributes("-topmost", True)

        search_frame = ctk.CTkFrame(self._win)
        search_frame.pack(fill="x", padx=10, pady=(10, 5))

        self._search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame, textvariable=self._search_var, placeholder_text="Поиск..."
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        search_btn = ctk.CTkButton(
            search_frame, text="Найти", width=80, command=self._refresh
        )
        search_btn.pack(side="right")

        self._textbox = ctk.CTkTextbox(self._win, wrap="word")
        self._textbox.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        self._refresh()

    def _refresh(self):
        search = self._search_var.get().strip() or None
        rows = get_history(limit=200, search=search)

        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")

        if not rows:
            self._textbox.insert("end", "Пусто.\n")
        else:
            for row in rows:
                _id, ts, dur, text, app = row
                ts_short = ts[:19].replace("T", " ")
                dur_str = f"{dur:.1f}s" if dur else ""
                header = f"[{ts_short}] {dur_str} ({app or '?'})"
                self._textbox.insert("end", f"{header}\n{text}\n\n")

        self._textbox.configure(state="disabled")
