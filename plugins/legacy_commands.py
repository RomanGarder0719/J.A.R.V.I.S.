import os
import subprocess
import time
import sys
import webbrowser
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

NAME = "legacy_commands"
KEYWORDS = ["открой", "запусти", "ютуб", "гугл", "браузер", "проект"]

# Маппинг команд на системные приложения
APPS = {
    'open_browser': lambda: webbrowser.open('https://google.com'),
    'open_youtube': lambda: webbrowser.open('https://youtube.com'),
    'open_google': lambda: webbrowser.open('https://google.com'),
    'adobe premiere': 'adobe premiere pro',
    'photoshop': 'photoshop',
    'kompas': 'kompas3d',
    'whatsapp': 'whatsapp',
    'vs code': 'code',
    'music': 'spotify',
    'music_off': lambda: None,  # Реализуется через mute
    'music_save': lambda: None,  # Заглушка
    'music_next': lambda: None,  # Заглушка
    'music_prev': lambda: None,  # Заглушка
}

# Маппинг для Windows системных команд
SYS_COMMANDS = {
    'open_terminal': 'cmd.exe',
    'clear_recycle_bin': 'powershell -command "Clear-RecycleBin -Force"',
    'minimize_all': 'powershell -command "(new-object -com shell.application).minimizeall()"',
}


def run(ctx, phrase: str):
    """Универсальная точка входа для PluginManager."""
    return handle_known(ctx, phrase, phrase)


def handle_known(ctx, cmd: str, voice: str) -> bool:
    """Выполняет команды по имени cmd или по ключевым словам."""

    # --- Обработка приложений ---
    if cmd in APPS:
        _launch_app(cmd)
        if cmd.startswith("music_"):
            time.sleep(0.2)
        if ctx.player:
            ctx.player.play_group("ok" if cmd != "open_project" else "project_1")
        return True

    # --- Веб-поиск ---
    v = voice.lower()

    if 'ютуб' in v:
        q = v.replace("джарвис", "").replace("на ютубе", "").replace("ютуб", "").strip()
        if q:
            webbrowser.open(f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}")
            if ctx.player:
                ctx.player.play_group("ok")
        else:
            webbrowser.open("https://youtube.com")
            if ctx.player:
                ctx.player.play_group("ok")
        return True

    if any(w in v for w in ['найди', 'поищи', 'загугли', 'ищи', 'в гугле', 'в интернете']):
        q = v.replace("джарвис", "").strip()
        for w in ['найди', 'поищи', 'загугли', 'ищи', 'в гугле', 'в интернете']:
            q = q.replace(w, '')
        if q:
            webbrowser.open(f"https://www.google.com/search?q={q.replace(' ', '+')}")
            if ctx.player:
                ctx.player.play_group("ok")
        else:
            webbrowser.open("https://google.com")
            if ctx.player:
                ctx.player.play_group("ok")
        return True

    # --- Системные команды ---
    if cmd == 'sound_off':
        _mute(True)
        if ctx.player:
            ctx.player.play_group("ok")
        return True

    if cmd == 'sound_on':
        _mute(False)
        if ctx.player:
            ctx.player.play_group("ok")
        return True

    if cmd == 'thanks':
        if ctx.player:
            ctx.player.play_group("thanks")
        return True

    if cmd == 'Start_game':
        # Замени на путь к своей игре
        game_path = r"C:\Games\Crysis\CryMP-Client64.exe"
        if os.path.exists(game_path):
            subprocess.Popen([game_path], creationflags=subprocess.CREATE_NO_WINDOW)
            if ctx.player:
                ctx.player.play_group("nerd")
        return True

    if cmd == 'stupid':
        if ctx.player:
            ctx.player.play_group("stupid")
        return True

    if cmd == 'restart':
        _restart_program(ctx)
        return True

    if cmd in SYS_COMMANDS:
        _run_system_command(cmd)
        if ctx.player:
            ctx.player.play_group("ok")
        return True

    if cmd == 'off':
        if ctx.player:
            ctx.player.play_group("off")
        os._exit(0)

    return False


def _launch_app(app_name: str):
    """Запускает приложение без видимого окна."""
    if callable(APPS[app_name]):
        APPS[app_name]()
        return

    try:
        # Пытаемся запустить через системный поиск
        subprocess.Popen([APPS[app_name]],
                         shell=True,
                         creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        # Fallback: открываем через стандартный запуск
        subprocess.Popen([app_name],
                         shell=True,
                         creationflags=subprocess.CREATE_NO_WINDOW)


def _run_system_command(cmd: str):
    """Выполняет системную команду без видимого окна."""
    subprocess.call(SYS_COMMANDS[cmd],
                    shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW)


def _mute(mute: bool):
    """Включение/выключение звука."""
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMute(int(mute), None)


def _restart_program(ctx):
    """Перезапуск программы."""
    if ctx.player:
        ctx.player.play_group("off")
    python = sys.executable
    os.execl(python, python, *sys.argv)