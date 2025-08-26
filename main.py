import json
import os
import queue
import random
import struct
import subprocess
import sys
import threading
import time
import tkinter as tk

from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from fuzzywuzzy import fuzz
from pvrecorder import PvRecorder
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from rich import print

import pvporcupine
import simpleaudio as sa
import vosk
import yaml
import config

from jarvis_gui import JarvisGUI
from jarvis_core import run_jarvis_core

# === Глобальные переменные ===
CDIR = os.getcwd()
VA_CMD_LIST = yaml.safe_load(open('commands.yaml', 'rt', encoding='utf8'))
SOUND_CACHE = {}
q = queue.Queue()
jarvis_core_started = False
recorder = None

# === Звуки ===
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
    "stupid": ["stupid.wav"]
}
for key, files in SOUND_MAP.items():
    for file in files:
        try:
            SOUND_CACHE[file] = sa.WaveObject.from_wave_file(os.path.join(CDIR, "sound", file))
        except Exception as e:
            print(f"[red]Ошибка загрузки {file}: {e}[/red]")

# === Инициализация wake word и модели ===
porcupine = pvporcupine.create(
    access_key=config.PICOVOICE_TOKEN,
    keywords=['jarvis'],
    sensitivities=[1]
)
model = vosk.Model("model_small")
samplerate = 16000
kaldi_rec = vosk.KaldiRecognizer(model, samplerate)

# === Звук ===
def play(phrase, wait_done=True):
    global recorder
    sounds = SOUND_MAP.get(phrase)
    if not sounds:
        print(f"[yellow]Звук '{phrase}' не найден[/yellow]")
        return
    sound_file = random.choice(sounds)
    wave_obj = SOUND_CACHE.get(sound_file)
    if not wave_obj:
        print(f"[red]Звук '{sound_file}' отсутствует в кэше[/red]")
        return
    if wait_done:
        recorder.stop()
    play_obj = wave_obj.play()
    if wait_done:
        play_obj.wait_done()
        recorder.start()

# === Распознавание команд ===
def filter_cmd(raw_voice: str):
    cmd = raw_voice.lower()
    for word in config.VA_ALIAS + config.VA_TBR:
        cmd = cmd.replace(word, '')
    return ' '.join(cmd.split())

def recognize_cmd(cmd: str):
    best_match = max(
        ((c, phrase, fuzz.ratio(cmd, phrase)) for c, phrases in VA_CMD_LIST.items() for phrase in phrases),
        key=lambda item: item[2],
        default=(None, None, 0)
    )
    return {'cmd': best_match[0] or '', 'percent': best_match[2]}

def mute_sound(mute: bool):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMute(int(mute), None)

def restart_program():
    play("off", True)
    porcupine.delete()
    recorder.stop()
    print("[yellow]Перезапуск...[/yellow]")
    python = sys.executable
    os.execl(python, python, *sys.argv)

def va_respond(voice: str):
    print(f"Распознано: {voice}")
    cleaned = filter_cmd(voice)
    cmd_data = recognize_cmd(cleaned)
    print(cmd_data)

    if cmd_data['percent'] >= 70 and cmd_data['cmd'] in VA_CMD_LIST:
        execute_cmd(cmd_data['cmd'], voice)
        return True

    # Поиск в YouTube / Google
    voice_lower = voice.lower()
    if any(word in voice_lower for word in ['найди', 'поищи', 'загугли', 'ищи', 'в гугле', 'в интернете', 'ютуб']):
        execute_cmd('search_web', voice)
        return True

    play("not_found1")
    return False

def with_microphone_restart(action):
    recorder.stop()
    try:
        action()
    finally:
        recorder.start()

# === Выполнение команд ===
def execute_cmd(cmd: str, voice: str):
    exe_commands = {
        'open_browser': 'Run browser.exe',
        'open_youtube': 'Run youtube.exe',
        'open_project': 'Open project.exe',
        'open_google': 'Run google.exe',
        'adobe premiere': 'Run adobe premiere.exe',
        'photoshop': 'Run photoshop.exe',
        'kompas': 'Run kompas.exe',
        'whatsapp': 'Run whatsapp.exe',
        'vs code': 'Run vs code.exe',
        'Task': 'Run Task.exe',
        'music': 'Run music.exe',
        'music_off': 'Stop music.exe',
        'music_save': 'Save music.exe',
        'music_next': 'Next music.exe',
        'music_prev': 'Prev music.exe',
    }

    if cmd in exe_commands:
        subprocess.Popen([os.path.join(CDIR, "custom-commands", exe_commands[cmd])])
        time.sleep(0.2 if cmd.startswith("music_") else 0)
        play("ok" if cmd != "open_project" else "project_1")
        return

    voice_lower = voice.lower()

    if 'ютуб' in voice_lower:
        query = voice_lower.replace("джарвис", "").replace("на ютубе", "").strip()
        if query:
            subprocess.Popen(['start', '', f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"], shell=True)
            play("ok")
        else:
            play("not_found1")
        return

    if any(w in voice_lower for w in ['найди', 'поищи', 'загугли', 'ищи', 'в гугле', 'в интернете']):
        query = voice_lower.replace("джарвис", "").strip()
        for w in ['найди', 'поищи', 'загугли', 'ищи', 'в гугле', 'в интернете']:
            query = query.replace(w, '')
        if query:
            subprocess.Popen(['start', '', f"https://www.google.com/search?q={query.replace(' ', '+')}"], shell=True)
            play("ok")
        else:
            play("not_found1")
        return

    if cmd == 'sound_off':
        play("ok")
        mute_sound(True)
    elif cmd == 'sound_on':
        mute_sound(False)
        play("ok")
    elif cmd == 'thanks':
        play("thanks")
    elif cmd == 'Start_game':
        subprocess.Popen([r"C:\Games\Crysis\CryMP-Client64.exe"])
        play("nerd")
    elif cmd == 'stupid':
        play("stupid")
    elif cmd == 'restart':
        restart_program()
    elif cmd == 'minimize_all':
        subprocess.call('powershell -command "(new-object -com shell.application).minimizeall()"', shell=True)
        play("ok")
    elif cmd == 'open_terminal':
        subprocess.Popen("start cmd", shell=True)
        play("ok")
    elif cmd == 'clear_recycle_bin':
        subprocess.call('powershell -command "Clear-RecycleBin -Force"', shell=True)
        play("ok")
    elif cmd == 'off':
        play("off", True)
        porcupine.delete()
        exit(0)

def restart_recorder():
    global recorder
    try:
        recorder.stop()
        recorder = PvRecorder(device_index=config.MICROPHONE_INDEX, frame_length=porcupine.frame_length)
        recorder.start()
        print("[green]Микрофон перезапущен[/green]")
        return True
    except Exception as e:
        print(f"[red]Ошибка микрофона: {e}[/red]")
        return False

def listen_for_command(timeout=10):
    ltc = time.time()
    while time.time() - ltc <= timeout:
        try:
            pcm = recorder.read()
        except OSError:
            print("[red]Ошибка доступа к микрофону[/red]")
            if not restart_recorder():
                break
            continue
        sp = struct.pack("h" * len(pcm), *pcm)
        if kaldi_rec.AcceptWaveform(sp):
            result = json.loads(kaldi_rec.Result())
            if va_respond(result["text"]):
                ltc = time.time()
            break

# === Старт ядра Jarvis (один раз) ===
def start_jarvis():
    global jarvis_core_started
    if not jarvis_core_started:
        threading.Thread(target=run_jarvis_core, daemon=True).start()
        jarvis_core_started = True

# === GUI и основная логика ===
def main():
    global recorder
    recorder = PvRecorder(device_index=config.MICROPHONE_INDEX, frame_length=porcupine.frame_length)
    recorder.start()

    print("[cyan]Jarvis v1.0 инициализирован[/cyan]")
    play("run_1")
    play("ready")
    play("project_1")

    print("[cyan]Сказать 'да' — открыть проект VS Code и музыку, 'нет' — открыть .docx заметки[/cyan]")

    while True:
        try:
            pcm = recorder.read()
            sp = struct.pack("h" * len(pcm), *pcm)
            if kaldi_rec.AcceptWaveform(sp):
                result = json.loads(kaldi_rec.Result())
                voice_input = result.get("text", "").lower()
                print(f"[magenta]Выбор:[/magenta] {voice_input}")
                if "да" in voice_input:
                    subprocess.Popen([r"C:\\Users\\Roman\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"])
                    subprocess.Popen([os.path.join(CDIR, "custom-commands", "Run music.exe")])
                    play("greet")
                    break
                elif "нет" in voice_input:
                    subprocess.Popen([os.path.join(CDIR, "custom-commands", "Open project.exe")])
                    play("run_2")
                    break
                else:
                    play("not_found1")
        except Exception as e:
            print(f"[red]Ошибка выбора: {e}[/red]")

    print("[cyan]Ожидание ключевой фразы 'джарвис'[/cyan]")
    while True:
        try:
            pcm = recorder.read()
            if porcupine.process(pcm) >= 0:
                with_microphone_restart(lambda: play("greet"))
                listen_for_command()
        except Exception as e:
            print(f"[red]Ошибка: {e}[/red]")

# === Точка входа ===
if __name__ == "__main__":
    root = tk.Tk()
    gui = JarvisGUI(root)
    threading.Thread(target=main, daemon=True).start()
    root.mainloop()
