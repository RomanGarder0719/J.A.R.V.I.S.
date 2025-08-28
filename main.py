import os
import sys
import json
import time
import struct
import threading
from rich import print
import tkinter as tk

import yaml
from fuzzywuzzy import fuzz

from core.audio import Recorder
from core.wake import WakeWord
from core.sounds import SoundPlayer
from core.commands_registry import CommandsRegistry
from plugin_manager import PluginManager
from ai.ai_handler import AIHandler
from jarvis_gui import JarvisGUI

import config  # ожидается: PICOVOICE_TOKEN, MICROPHONE_INDEX, VA_ALIAS, VA_TBR

# === Глобальные одноразовые сервисы ===
player = SoundPlayer(sound_dir=os.path.join(os.getcwd(), "sound"))
recorder = None
wake = None
stt = None
registry = None
plugins = None
ai = None


def init_services():
    global recorder, wake, stt, registry, plugins, ai

    # Wake-word
    wake = WakeWord("model_small",config.VA_ALIAS,config.MICROPHONE_INDEX)

    # Микрофон
    recorder = Recorder("model_small") #(device_index=config.MICROPHONE_INDEX)
    recorder.start()


    # СТТ (Vosk)
    #stt = VoskSTT(model_path="model_small", sample_rate=16000)

    # YAML-реестр команд (старый список с нечётким поиском)
    registry = CommandsRegistry(path="commands.yaml", aliases=config.VA_ALIAS, tbr=config.VA_TBR)

    # Плагины
    plugins = PluginManager(player=player)

    # GPT-логика
    ai = AIHandler(player=player, plugins=plugins)


def stop_services():
    try:
        recorder.stop()
    except Exception:
        pass
    try:
        wake.close()
    except Exception:
        pass


def listen_once(timeout_sec=10):
    """Слушаем фразу после пробуждения; ограничиваемся по времени."""
    deadline = time.time() + timeout_sec
    recorder.reset()
    while time.time() < deadline:
        chunk = recorder.read()
        if not chunk:
            continue

        if recorder.accept(chunk):
            text = recorder.result_text()
            if text:
                return text
    return ""


def handle_text(raw_text: str):
    print(f"[cyan]Распознано:[/cyan] {raw_text}")

    # 1) Очистка от обращений и служебных слов
    cleaned = registry.filter_text(raw_text)

    # 2) Поиск совпадения в YAML-командах
    match = registry.best_match(cleaned)
    if match.percent >= 70 and match.cmd:
        print(f"[green]Команда из YAML:[/green] {match.cmd} ({match.percent}%)")
        # Встроенный плагин legacy обработает известные команды
        if plugins.execute_known(match.cmd, raw_text):
            player.play_group("ok")
            return True

    # 3) Поиск среди Python-плагинов
    if plugins.execute_by_phrase(raw_text):
        return True

    # 4) GPT: ответить или сгенерировать новый плагин
    return ai.handle_phrase(raw_text)


def main_loop():

    #player.play_group("run_1")
    player.play_group("ready")


    print("[cyan]Ожидание ключевой фразы 'джарвис'[/cyan]")

    while True:
        try:
            #pcm = recorder.read()
            if wake.listen():
                # краткий звук подтверждения
                recorder.pause(lambda: player.play_group("greet"))

                text = listen_once(timeout_sec=10)
                if not text:
                    player.play_group("not_found1")
                    continue

                handled = handle_text(text)
                if not handled:
                    player.play_group("not_found1")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[red]Ошибка цикла: {e}[/red]")


if __name__ == "__main__":
    init_services()

    root = tk.Tk()
    gui = JarvisGUI(root)

    worker = threading.Thread(target=main_loop, daemon=True)
    worker.start()

    try:
        root.mainloop()
    finally:
        stop_services()
