import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import yaml
import os

COMMANDS_FILE = "commands.yaml"

class CommandEditor(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Редактор команд")
        self.geometry("600x500")
        self.configure(bg="black")
        self.resizable(False, False)

        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=("Consolas", 11), bg="#1e1e1e", fg="white", insertbackground="white")
        self.text_area.pack(expand=True, fill="both", padx=10, pady=10)

        self.load_commands()

        btn_frame = tk.Frame(self, bg="black")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="💾 Сохранить", command=self.save_commands, bg="#303030", fg="white", font=("Segoe UI", 10), width=15).pack(side="left", padx=10)
        tk.Button(btn_frame, text="⟲ Отменить", command=self.destroy, bg="#303030", fg="white", font=("Segoe UI", 10), width=15).pack(side="left", padx=10)

    def load_commands(self):
        if os.path.exists(COMMANDS_FILE):
            with open(COMMANDS_FILE, 'r', encoding="utf-8") as f:
                content = f.read()
            self.text_area.insert(tk.END, content)
        else:
            self.text_area.insert(tk.END, "# Здесь будут ваши команды")

    def save_commands(self):
        try:
            yaml.safe_load(self.text_area.get("1.0", tk.END))  # Проверка на ошибки
            with open(COMMANDS_FILE, 'w', encoding="utf-8") as f:
                f.write(self.text_area.get("1.0", tk.END))
            messagebox.showinfo("Успех", "Команды успешно сохранены.")
            self.destroy()
        except yaml.YAMLError as e:
            messagebox.showerror("Ошибка YAML", f"Ошибка в синтаксисе YAML:\n\n{e}")
