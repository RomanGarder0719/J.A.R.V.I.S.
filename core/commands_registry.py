import yaml
from dataclasses import dataclass
from fuzzywuzzy import fuzz

@dataclass
class Match:
    cmd: str
    percent: int

class CommandsRegistry:
    """Поиск по старому YAML-списку команд. Ожидается формат: {cmd: [phrases...]}"""

    def __init__(self, path: str, aliases: list[str], tbr: list[str]):
        self._path = path
        self._aliases = aliases
        self._tbr = tbr
        try:
            with open(path, 'rt', encoding='utf-8') as f:
                self._data = yaml.safe_load(f) or {}
        except Exception:
            self._data = {}

    def filter_text(self, text: str) -> str:
        t = text.lower()
        # удаляем обращения типа "джарвис" и шаблонные слова
        for w in self._aliases + self._tbr:
            t = t.replace(w, '')
        return ' '.join(t.split())

    def best_match(self, cleaned: str) -> Match:
        best = ("", 0)
        for c, phrases in self._data.items():
            for p in phrases:
                score = fuzz.ratio(cleaned, p)
                if score > best[1]:
                    best = (c, score)
        return Match(cmd=best[0], percent=best[1])