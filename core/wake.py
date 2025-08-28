from core.audio import Recorder
from rich import print

class WakeWord:
    """
    Слушает микрофон через Recorder.
    - wakewords: tuple[str], например ("джарвис", "слушай друг")
    - возвращает PCM-байты, когда найден wakeword
    """

    def __init__(self, model_path: str, wakewords: tuple[str], device_index: int = -1):
        if not isinstance(wakewords, tuple):
            raise ValueError("wakewords должен быть tuple, например ('джарвис', 'алиса')")
        self._wakewords = tuple(w.lower() for w in wakewords)
        self._recorder = Recorder(model_path, device_index=device_index)
        self._running = False

    def start(self):
        self._recorder.start()
        self._running = True
        print(f"[green]WakeWordDetector запущен, слушаю: {self._wakewords}[/green]")

    def stop(self):
        self._recorder.stop()
        self._running = False
        print("[yellow]WakeWordDetector остановлен[/yellow]")

    def listen(self) -> bytes | None:
        self.start()
        try:
            while self._running:
                chunk = self._recorder.read()
                if not chunk:
                    continue
                if self._recorder.accept(chunk):
                    text = self._recorder.result_text().lower()
                    if text:
                        print(f"[cyan]Распознано: {text}[/cyan]")
                        for word in self._wakewords:
                            if word in text:
                                print(f"[green]Найден wakeword: {word}[/green]")
                                return chunk  # ⚡ возвращаем bytes PCM
        finally:
            self.stop()
