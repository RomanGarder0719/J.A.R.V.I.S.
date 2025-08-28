import sounddevice as sd
import numpy as np
import threading
import json
from vosk import Model, KaldiRecognizer
from collections import deque
from rich import print

class Recorder:
    """
    Микрофон + Vosk STT.
    - read() возвращает bytes PCM int16
    - accept(bytes) и result_text() как VoskSTT
    """

    def __init__(self, model_path: str, device_index: int = -1, frame_length: int = 160, samplerate: int = 16000):
        self._frame = frame_length
        self._idx = None if device_index == -1 else device_index
        self._samplerate = samplerate
        self._queue = deque(maxlen=100)
        self._lock = threading.Lock()
        self._stream = None
        self._running = False

        # Vosk
        self._model = Model(model_path)
        self._rec = KaldiRecognizer(self._model, self._samplerate)

    def start(self):
        if self._running:
            return

        def callback(indata, frames, time, status):
            if status:
                print(f"[yellow]Audio status: {status}[/yellow]")
            try:
                with self._lock:
                    self._queue.append((indata[:, 0] * 32767).astype(np.int16).tobytes())
            except Exception as e:
                print(f"[red]Ошибка в audio callback: {e}[/red]")

        self._stream = sd.InputStream(
            device=self._idx,
            channels=1,
            samplerate=self._samplerate,
            blocksize=self._frame,
            dtype='float32',
            callback=callback
        )
        self._stream.start()
        self._running = True
        print(f"[green]Recorder+STT started on device {self._idx}[/green]")

    def stop(self):
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception as e:
                print(f"[red]Ошибка остановки потока: {e}[/red]")
            finally:
                self._stream = None
        self._running = False
        print("[yellow]Recorder stopped[/yellow]")

    def read(self):
        with self._lock:
            if self._queue:
                return self._queue.popleft()
            return None

    # --- Vosk API ---
    def reset(self):
        self._rec = KaldiRecognizer(self._model, self._samplerate)

    def accept(self, chunk_bytes: bytes) -> bool:
        return self._rec.AcceptWaveform(chunk_bytes)

    def result_text(self) -> str:
        try:
            data = json.loads(self._rec.Result())
            return (data.get("text") or "").strip()
        except Exception:
            return ""

    def pause(self, action):
        """Остановить аудиопоток, выполнить action, запустить снова."""
        self.stop()
        try:
            action()
        finally:
            self.start()
