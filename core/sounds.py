import os
import random
import simpleaudio as sa
from rich import print

SOUND_MAP = {
    "greet": [f"greet{n}.wav" for n in range(1, 4)],
    "ok": [f"ok{n}.wav" for n in range(1, 5)],
    "not_found1": ["not_found1.wav"],
    "thanks": ["thanks.wav"],
    "project_1": ["project_1.wav"],
    "run_1": ["run_1.wav"],
    "run_2": ["run_2.wav"],
    "ready": ["ready.wav"],
    "nerd": ["nerd.wav"],
    "off": ["off.wav"],
    "stupid": ["stupid.wav"],
}

class SoundPlayer:
    def __init__(self, sound_dir: str):
        self._dir = sound_dir
        self._cache = {}
        for key, files in SOUND_MAP.items():
            for fname in files:
                path = os.path.join(self._dir, fname)
                try:
                    self._cache[fname] = sa.WaveObject.from_wave_file(path)
                except Exception as e:
                    print(f"[red]Ошибка загрузки {fname}: {e}[/red]")

    def play_group(self, group: str):
        files = SOUND_MAP.get(group)
        if not files:
            return
        fname = random.choice(files)
        wave = self._cache.get(fname)
        if wave:
            wave.play()