import numpy as np
import sounddevice as sd
import threading


class Recorder:
    def __init__(self, sample_rate=16000, channels=1, device=None):
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device
        self._chunks = []
        self._stream = None
        self._recording = False
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            if self._recording:
                return
            self._chunks = []
            try:
                self._stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    dtype="float32",
                    device=self.device,
                    callback=self._callback,
                    blocksize=1024,
                )
                self._recording = True
                self._stream.start()
            except Exception:
                self._stream = None
                self._recording = False
                raise

    def stop(self):
        with self._lock:
            if not self._recording:
                return None
            self._recording = False
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            if not self._chunks:
                return None
            audio = np.concatenate(self._chunks, axis=0).flatten()
            self._chunks = []
            return audio

    def _callback(self, indata, frames, time_info, status):
        if self._recording:
            self._chunks.append(indata.copy())

    @property
    def is_recording(self):
        return self._recording
