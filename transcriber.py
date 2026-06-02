import os
import sys
import threading
from faster_whisper import WhisperModel

BASE_DIR = os.path.dirname(__file__)


class Transcriber:
    def __init__(self, model_size="large-v3", device="cuda", compute_type="float16"):
        # If model_size is a relative path that exists locally, use it
        local_path = os.path.join(BASE_DIR, model_size)
        if os.path.isdir(local_path):
            self.model_size = local_path
        else:
            self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        # macOS не поддерживает CUDA (CTranslate2 работает только на CPU)
        if sys.platform == "darwin" and self.device != "cpu":
            self.device = "cpu"
            self.compute_type = "int8"
        self.model = None
        self._lock = threading.Lock()

    def load_model(self):
        print(f"[Transcriber] Loading {self.model_size} on {self.device}...")
        try:
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
            if self.device != "cpu":
                self._warmup()  # прогрев: ошибки cublas/cudnn вылезут тут, а не при первой диктовке
        except Exception as e:
            if self.device == "cpu":
                raise
            print(f"[Transcriber] {self.device} недоступен ({e}). Переключаюсь на CPU/int8.")
            self.device = "cpu"
            self.compute_type = "int8"
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
        print(f"[Transcriber] Model loaded on {self.device}.")

    def _warmup(self):
        """Крошечный инференс, чтобы GPU-библиотеки (cublas/cudnn) реально
        загрузились и их отсутствие поймалось здесь, а не при первой диктовке."""
        import numpy as np
        dummy = (np.random.randn(16000).astype("float32") * 0.01)
        segments, _ = self.model.transcribe(dummy, language="ru", beam_size=1, vad_filter=False)
        for _ in segments:
            pass

    def transcribe(self, audio_np, sample_rate=16000):
        with self._lock:
            segments, info = self.model.transcribe(
                audio_np,
                language="ru",
                beam_size=5,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
            )
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text.strip())
            return " ".join(text_parts)
