import tkinter as tk
from tkinter import ttk, messagebox
import json
import time
import threading
import os
from datetime import datetime
from pygame import mixer
import subprocess

TRAINING_PROGRAM = {
    "День 1": {
        "Спина": [
            {"name": "Подтяг с полотенцем", "level": 1, "reps": 10},
            {"name": "Тяга полотенца лёжа", "level": 2, "reps": 12},
            {"name": "Супермен с полотенцем", "level": 3, "reps": 15}
        ]
    },
    "День 2": {
        "Грудь": [
            {"name": "Отжимания", "level": 1, "reps": 12},
            {"name": "Жим от пола узким хватом", "level": 2, "reps": 10}
        ]
    }
}

SAVE_FILE = "training_data.json"
MUSIC_PATH = "workout_music.mp3"

class TrainingModule:
    def __init__(self, root):
        self.root = root
        self.root.title("Тренировка")

        mixer.init()
        self.try_play_music()

        self.days = list(TRAINING_PROGRAM.keys())
        self.current_day_index = 0
        self.blocks = []
        self.current_block_index = 0

        self.exercises = []
        self.exercise_index = 0
        self.current_data = {}

        self.setup_ui()
        self.load_data()
        self.update_day()

    def setup_ui(self):
        bg_image = tk.PhotoImage(file="background_jarvis.png") if os.path.exists("background_jarvis.png") else None
        if bg_image:
            background_label = tk.Label(self.root, image=bg_image)
            background_label.image = bg_image
            background_label.place(relwidth=1, relheight=1)

        # Навигация по дням
        self.day_label = tk.Label(self.root, text="", font=("Arial", 14, "bold"))
        self.day_label.pack(pady=5)
        day_nav = tk.Frame(self.root)
        day_nav.pack()
        tk.Button(day_nav, text="< День", command=self.prev_day).pack(side=tk.LEFT, padx=10)
        tk.Button(day_nav, text="День >", command=self.next_day).pack(side=tk.LEFT, padx=10)

        # Навигация по блокам
        self.block_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.block_label.pack(pady=5)
        block_nav = tk.Frame(self.root)
        block_nav.pack()
        tk.Button(block_nav, text="< Блок", command=self.prev_block).pack(side=tk.LEFT, padx=10)
        tk.Button(block_nav, text="Блок >", command=self.next_block).pack(side=tk.LEFT, padx=10)

        # Упражнение
        self.exercise_frame = tk.Frame(self.root)
        self.exercise_frame.pack(pady=10)

        self.exercise_label = tk.Label(self.exercise_frame, text="", font=("Arial", 16, "bold"))
        self.exercise_label.pack()

        nav = tk.Frame(self.exercise_frame)
        nav.pack()
        tk.Button(nav, text="<", command=self.prev_exercise).pack(side=tk.LEFT)
        tk.Button(nav, text=">", command=self.next_exercise).pack(side=tk.RIGHT)

        # Таблица подходов
        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(pady=10)

        headers = ["Пред. вес", "Повторы", "Вес (кг)", "Готово"]
        for idx, h in enumerate(headers):
            tk.Label(self.table_frame, text=h, font=("Arial", 10, "bold"), bg="#1a1a1a", fg="white").grid(row=0, column=idx)

        self.rows = []
        for i in range(4):
            row = {}
            row['prev'] = tk.Label(self.table_frame, text="0")
            row['prev'].grid(row=i+1, column=0)

            row['reps'] = ttk.Entry(self.table_frame, width=5)
            row['reps'].grid(row=i+1, column=1)
            row['reps'].insert(0, "0")

            row['weight'] = ttk.Entry(self.table_frame, width=5)
            row['weight'].grid(row=i+1, column=2)

            row['check_var'] = tk.BooleanVar()
            row['check'] = ttk.Checkbutton(self.table_frame, variable=row['check_var'],
                                   command=lambda i=i: self.start_timer(i))
            row['check'].grid(row=i+1, column=3)

            self.rows.append(row)



        self.timer_label = tk.Label(self.root, text="", font=("Arial", 12), fg="cyan")
        self.timer_label.pack(pady=5)

        self.finish_button = tk.Button(self.root, text="Завершить упражнение", command=self.finish_exercise)
        self.finish_button.pack(pady=10)

    def try_play_music(self):
        try:
            aimp_path = r"C:\\Program Files\\AIMP\\AIMP.exe"
            if os.path.exists(aimp_path):
                subprocess.Popen([aimp_path])
        except Exception as e:
            print(f"Ошибка запуска AIMP: {e}")

    def update_day(self):
        if not self.days:
            return
        self.current_day = self.days[self.current_day_index]
        self.day_label.config(text=f"{self.current_day}")
        self.blocks = list(TRAINING_PROGRAM[self.current_day].keys())
        self.current_block_index = 0
        self.update_block()

    def prev_day(self):
        if self.current_day_index > 0:
            self.current_day_index -= 1
            self.update_day()

    def next_day(self):
        if self.current_day_index < len(self.days) - 1:
            self.current_day_index += 1
            self.update_day()

    def update_block(self):
        if not self.blocks:
            return
        self.current_block = self.blocks[self.current_block_index]
        self.block_label.config(text=f"{self.current_block}")
        self.exercises = TRAINING_PROGRAM[self.current_day][self.current_block]
        self.exercise_index = 0
        self.update_ui()

    def prev_block(self):
        if self.current_block_index > 0:
            self.current_block_index -= 1
            self.update_block()

    def next_block(self):
        if self.current_block_index < len(self.blocks) - 1:
            self.current_block_index += 1
            self.update_block()

    def update_ui(self):
        if not self.exercises:
            return
        ex = self.exercises[self.exercise_index]
        self.exercise_label.config(text=f"{ex['name']} (Уровень {ex['level']})")
        for row in self.rows:
            row['prev'].config(text="0")
            row['reps'].config(text=str(ex['reps']))
            row['weight'].delete(0, tk.END)
            row['weight'].insert(0, "0")
            row['check_var'].set(False)
        self.timer_label.config(text="")

    def prev_exercise(self):
        if self.exercise_index > 0:
            self.exercise_index -= 1
            self.update_ui()

    def next_exercise(self):
        if self.exercise_index < len(self.exercises) - 1:
            self.exercise_index += 1
            self.update_ui()

    def start_timer(self, row_index):
        def timer_thread():
            self.timer_label.config(text="Отдых 2:00")
            for i in range(120, 0, -1):
                self.timer_label.config(text=f"Отдых {i//60}:{i%60:02d}")
                time.sleep(1)
            self.timer_label.config(text="Готов к следующему подходу")
        threading.Thread(target=timer_thread, daemon=True).start()

    def finish_exercise(self):
        ex = self.exercises[self.exercise_index]
        date_key = datetime.now().strftime("%Y-%m-%d")
        self.current_data.setdefault(date_key, {})[ex['name']] = {
    'level': ex['level'],
    'reps': [row['reps'].get() for row in self.rows],
    'weights': [row['weight'].get() for row in self.rows],
    'timestamp': datetime.now().strftime("%H:%M")
}
        self.save_data()
        messagebox.showinfo("Готово", "Упражнение сохранено.")

    def save_data(self):
        with open(SAVE_FILE, 'w') as f:
            json.dump(self.current_data, f, indent=4)

    def load_data(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r') as f:
                self.current_data = json.load(f)
def launch_aimp():
    try:
        aimp_path = r"C:\\Program Files\\AIMP\\AIMP.exe"
        if os.path.exists(aimp_path):
            subprocess.Popen([aimp_path])
        else:
            print("AIMP не найден.")
    except Exception as e:
        print(f"Ошибка запуска AIMP: {e}")
if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingModule(root)
    root.mainloop()

# --- ЗАПУСК AIMP (опционально) ---

