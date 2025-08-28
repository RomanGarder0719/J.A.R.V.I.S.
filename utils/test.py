import sounddevice as sd
import queue
import vosk
import json

# === Настройки ===
WAKEWORD = "джарвис"
MODEL_PATH = "../model_small"  # путь к распакованной модели Vosk

# === Очередь для аудио ===
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print("Ошибка записи:", status)
    q.put(bytes(indata))  # у RawInputStream это уже bytes (int16)

def main():
    model = vosk.Model(MODEL_PATH)
    rec = vosk.KaldiRecognizer(model, 16000)

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                           channels=1, callback=callback):
        print("🎙 Скажи 'джарвис' для теста...")
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").lower()
                if text:
                    print("Vosk услышал:", text)
                if WAKEWORD in text:
                    print("🚀 Wakeword сработал!")
                    break
            else:
                partial = json.loads(rec.PartialResult())
                if WAKEWORD in partial.get("partial", "").lower():
                    print("🚀 Wakeword (partial) сработал!")
                    break

if __name__ == "__main__":
    main()
