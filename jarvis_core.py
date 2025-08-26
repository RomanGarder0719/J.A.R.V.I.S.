import threading
import time
import random
import os
import simpleaudio as sa

# === Флаг активности ядра ===
is_running = False

# === Звуки и фразы (по желанию можно вынести в общую config-функцию) ===
SOUND_DIR = os.path.join(os.getcwd(), "sound")
SOUNDS = {
    "thinking": ["thinking1.wav", "thinking2.wav"],
    "processing": ["processing1.wav", "processing2.wav"],
    "error": ["not_found1.wav"],
    "idle": ["ready.wav"]
}

def play_sound(name):
    if name not in SOUNDS:
        print(f"[JarvisCore] Звук '{name}' не найден.")
        return
    file = random.choice(SOUNDS[name])
    path = os.path.join(SOUND_DIR, file)
    try:
        sound = sa.WaveObject.from_wave_file(path)
        sound.play()
    except Exception as e:
        print(f"[JarvisCore] Ошибка воспроизведения звука {file}: {e}")

# === Основная логика ядра ===
def jarvis_core_loop():
    print("[JarvisCore] Ядро запущено.")

    while is_running:
        try:
            # Здесь можно добавить обработку памяти, мыслей, или генерацию логов
            time.sleep(5)
            print("[JarvisCore] Ожидаю событий...")  # Можно заменить на реальный поток размышлений
        except Exception as e:
            print(f"[JarvisCore] Ошибка: {e}")
            play_sound("error")
            time.sleep(2)

    print("[JarvisCore] Ядро завершено.")

# === Запуск ядра (вызывается из main.py) ===
def run_jarvis_core():
    global is_running

    if is_running:
        print("[JarvisCore] Уже работает.")
        return

    is_running = True
    threading.Thread(target=jarvis_core_loop, daemon=True).start()
