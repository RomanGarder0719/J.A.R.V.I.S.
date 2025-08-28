import os
import importlib.util
from typing import Callable

class PluginManager:
    """Поиск/выполнение Python-плагинов. Плагины должны иметь: NAME, KEYWORDS(list), run(ctx, phrase)."""

    def __init__(self, plugins_dir: str = "plugins", player=None):
        self._dir = plugins_dir
        self._player = player
        self._mods = {}
        os.makedirs(self._dir, exist_ok=True)
        self.reload()

    def _load_file(self, path: str):
        name = os.path.splitext(os.path.basename(path))[0]
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # может бросить исключение — пусть видно в логах
        if not hasattr(mod, "NAME") or not hasattr(mod, "KEYWORDS") or not hasattr(mod, "run"):
            raise ValueError(f"Плагин {name} не соответствует интерфейсу")
        self._mods[name] = mod

    def reload(self):
        self._mods.clear()
        for fn in os.listdir(self._dir):
            if not fn.endswith(".py") or fn == "__init__.py":
                continue
            self._load_file(os.path.join(self._dir, fn))
    def execute_by_phrase(self, phrase: str) -> bool:
        p = phrase.lower()
        for mod in self._mods.values():
            try:
                if any(kw in p for kw in getattr(mod, "KEYWORDS", [])):
                    mod.run(self._context(), phrase)
                    return True
            except Exception as e:
                print(f"[red]Ошибка плагина {getattr(mod, 'NAME', '?')}: {e}[/red]")
        return False

    def execute_known(self, cmd: str, raw_text: str) -> bool:
        """Для обратной совместимости: известные команды из старого списка."""
        if "legacy_commands" in self._mods:
            try:
                return self._mods["legacy_commands"].handle_known(self._context(), cmd, raw_text)
            except Exception as e:
                print(f"[red]Ошибка legacy: {e}[/red]")
        return False

    def add_plugin(self, filename: str, code: str):
        path = os.path.join(self._dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        self._load_file(path)

    # --- вспомогательный контекст ---
    def _context(self):
        class Ctx:
            player = self._player
        return Ctx()