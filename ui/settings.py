import json
import os
import customtkinter as ctk

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
DICT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dictionary.json")


class SettingsWindow:
    def __init__(self, on_config_changed=None):
        self._win = None
        self.on_config_changed = on_config_changed

    def _load_config(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_config(self, cfg):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)

    def _load_dict(self):
        if not os.path.exists(DICT_PATH):
            return {}
        with open(DICT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_dict(self, d):
        with open(DICT_PATH, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)

    def show(self):
        if self._win and self._win.winfo_exists():
            self._win.focus()
            return

        cfg = self._load_config()

        self._win = ctk.CTkToplevel()
        self._win.title("VoiceKey — Настройки")
        self._win.geometry("500x550")
        self._win.attributes("-topmost", True)

        # Model size
        ctk.CTkLabel(self._win, text="Модель:").pack(anchor="w", padx=15, pady=(15, 0))
        self._model_var = ctk.StringVar(value=cfg.get("model_size", "large-v3"))
        ctk.CTkOptionMenu(
            self._win,
            variable=self._model_var,
            values=["tiny", "base", "small", "medium", "large-v3"],
        ).pack(fill="x", padx=15, pady=5)

        # Double press threshold
        ctk.CTkLabel(self._win, text="Порог двойного нажатия (мс):").pack(
            anchor="w", padx=15, pady=(10, 0)
        )
        self._threshold_var = ctk.StringVar(
            value=str(cfg.get("double_press_threshold_ms", 300))
        )
        ctk.CTkEntry(self._win, textvariable=self._threshold_var).pack(
            fill="x", padx=15, pady=5
        )

        # Dictionary
        ctk.CTkLabel(self._win, text="Словарь замен (слово = замена, по одной на строку):").pack(
            anchor="w", padx=15, pady=(15, 0)
        )
        self._dict_textbox = ctk.CTkTextbox(self._win, height=200)
        self._dict_textbox.pack(fill="both", expand=True, padx=15, pady=5)

        d = self._load_dict()
        for k, v in d.items():
            self._dict_textbox.insert("end", f"{k} = {v}\n")

        # Save button
        ctk.CTkButton(self._win, text="Сохранить", command=self._save).pack(
            pady=15
        )

    def _save(self):
        cfg = self._load_config()
        cfg["model_size"] = self._model_var.get()
        try:
            cfg["double_press_threshold_ms"] = int(self._threshold_var.get())
        except ValueError:
            pass
        self._save_config(cfg)

        # Parse dictionary
        text = self._dict_textbox.get("1.0", "end").strip()
        d = {}
        for line in text.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip()
                if k and v:
                    d[k] = v
        self._save_dict(d)

        if self.on_config_changed:
            self.on_config_changed(cfg)

        self._win.destroy()
