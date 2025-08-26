import tkinter as tk
from tkinter import ttk
from tkinter import Label, Frame
from PIL import Image, ImageTk, ImageSequence
from command_editor import CommandEditor
from training_music_module import TrainingModule, launch_aimp
import threading
import ctypes


class JarvisGUI:
    def __init__(self, root):
        self.root = root
        close_btn = tk.Button(root, text="✕", command=root.destroy, bg="black", fg="red", bd=0, font=("Segoe UI", 10))
        close_btn.place(relx=0.97, rely=0.005, anchor="ne")
        minimize_btn = tk.Button(root, text="━", command=self.minimize_window, bg="black", fg="white", bd=0, font=("Segoe UI", 10))
        minimize_btn.place(relx=0.93, rely=0.005, anchor="ne")
    
        self.root.title("J.A.R.V.I.S.")
        self.root.geometry("600x720")
    
        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            style = ctypes.windll.dwmapi.DwmSetWindowAttribute
            attr = 2  # DWMWA_WINDOW_CORNER_PREFERENCE
            preference = ctypes.c_int(2)  # DWMWCP_ROUND
            style(hwnd, attr, ctypes.byref(preference), ctypes.sizeof(preference))
        except Exception as e:
            print("Округление не поддерживается:", e)

        self.root.configure(bg="black")
        self.root.after(10, lambda: self.root.overrideredirect(True))

        # Восстановление рамки при сворачивании, чтобы можно было развернуть
        self.root.bind("<Unmap>", lambda e: self.root.overrideredirect(False))
        self.root.bind("<Map>", lambda e: self.root.after(10, lambda: self.root.overrideredirect(True)))


        # Перетаскивание окна
        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)
        self.create_right_menu()

    def create_right_menu(self):

        def on_hover(e): e.widget.config(fg="#00ffff")
        def on_leave(e): e.widget.config(fg="white")

        self.right_menu_frame = Frame(self.root, width=200, bg="#101820", height=720)
        self.right_menu_frame.place(x=600, y=40)  # Изначально за пределами окна


        listen_btn = tk.Button(
            self.right_menu_frame,
            text="🎙 Прослушивание",
            command=self.listen_action,
            fg="white",
            bg="#101820",
            font=("Segoe UI", 11, "bold"),
            bd=0,
            activebackground="#1f1f2e",
            activeforeground="#00ffff",
            cursor="hand2"
    )
        listen_btn.pack(pady=20, anchor="center", padx=30)
        listen_btn.bind("<Enter>", on_hover)
        listen_btn.bind("<Leave>", on_leave)

        music_btn = tk.Button(
            self.right_menu_frame,
            text="🎵 Музыка",
            command=self.music_action,
            fg="white",
            bg="#101820",
            font=("Segoe UI", 11, "bold"),
            bd=0,
            activebackground="#1f1f2e",
            activeforeground="#00ffff",
            cursor="hand2"
    )
        music_btn.pack(pady=10, anchor="center", padx=30)
        music_btn.bind("<Enter>", on_hover)
        music_btn.bind("<Leave>", on_leave)

        self.right_menu_visible = False
        self.root.bind("<Motion>", self.check_mouse_position_extended)

        self.create_main_content()
        self.create_sidebar_menu()
        self.pulse_neon()

    def minimize_window(self):
        self.root.overrideredirect(False)
        self.root.iconify()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        x = event.x_root - self.x
        y = event.y_root - self.y
        self.root.geometry(f"+{x}+{y}")

    def create_main_content(self):
        self.center_frame = Frame(self.root, bg="black")
        self.center_frame.pack(expand=True)

        self.gif_label = Label(self.center_frame, bg="black")
        self.gif_label.pack()

        self.jarvis_text = Label(self.root, text="J.A.R.V.I.S.", font=("Orbitron", 20), bg="black", fg="#00FFFF")
        self.jarvis_text.pack(pady=30, side="bottom")

        self.load_gif("jarvis.gif")

    def load_gif(self, gif_path):
        gif = Image.open(gif_path)
        resized_frames = []
        for frame in ImageSequence.Iterator(gif):
            resized = frame.copy().convert('RGBA').resize((250, 250), Image.LANCZOS)  # ← уменьшаем до 250x250
            resized_frames.append(ImageTk.PhotoImage(resized))
        self.gif_frames = resized_frames

        self.gif_index = 0
        self.animate_gif()

    def animate_gif(self):
        frame = self.gif_frames[self.gif_index]
        self.gif_label.configure(image=frame)
        self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
        self.root.after(50, self.animate_gif)  # fps control

    def create_sidebar_menu(self):
        self.menu_frame = Frame(self.root, width=200, bg="#101820", height=720)
        self.menu_frame.place(x=-200, y=40)

    # Список: название и соответствующая команда
        options = [
            ("Редактор команд", lambda: CommandEditor(self.root)),
           ("Фокус-режим",lambda: print("Focus")),
            ("Тренировки", lambda: TrainingModule(tk.Toplevel(self.root))),
            ("Питание", lambda: print("Питание")),
            ("Идеи", lambda: print("Идеи")),
            ("Настройки", lambda: print("Настройки")),
            ("Музыка", launch_aimp)
    ]

    # Отображаем пункты меню
        for text, command in options:
            lbl = Label(self.menu_frame, text=text, fg="white", bg="#101820", font=("Arial", 12), pady=10, cursor="hand2")
            lbl.pack(anchor="w", padx=30)
            lbl.bind("<Button-1>", lambda e, cmd=command: cmd())

        self.menu_visible = False
        self.root.bind("<Motion>", self.check_mouse_position_extended)


    def check_mouse_position_extended(self, event):
    # Левое меню
        if event.x < 10 and not self.menu_visible:
            self.show_menu()
        elif event.x > 220 and self.menu_visible:
            self.hide_menu()

    # Правое меню
        if event.x > self.root.winfo_width() - 10 and not self.right_menu_visible:
            self.show_right_menu()
        elif event.x < self.root.winfo_width() - 220 and self.right_menu_visible:
            self.hide_right_menu()

    def show_right_menu(self):
        self.right_menu_visible = True
        self.slide_right_menu(visible=True)

    def hide_right_menu(self):
        self.right_menu_visible = False
        self.slide_right_menu(visible=False)

    def slide_right_menu(self, visible):
        def animate():
            start = self.root.winfo_width()  # 600
            end = self.root.winfo_width() - 200  # 400
            for i in range(21):
                offset = int(i * (200 / 20))
                new_x = (start - offset) if visible else (end + offset)
                self.right_menu_frame.place(x=new_x, y=40)
                self.root.update()
                self.root.after(5)
        threading.Thread(target=animate).start()

    def listen_action(self):
        print("🎙 Прослушивание активировано")

    def music_action(self):
        print("🎵 Музыка включена")


    def show_menu(self):
        self.menu_visible = True
        self.slide_menu(visible=True)

    def hide_menu(self):
        self.menu_visible = False
        self.slide_menu(visible=False)

    def slide_menu(self, visible):
        def animate():
            x = -200 if not visible else 0
            for i in range(21):
                offset = int(i * (200 / 20))
                new_x = -200 + offset if visible else 0 - offset
                self.menu_frame.place(x=new_x, y=40)  # ← отступ 40 пикселей
                self.root.update()
                self.root.after(5)
        threading.Thread(target=animate).start()

    def pulse_neon(self):
        self.neon_phase = 0
        self.neon_direction = 1

        def update_color():
            intensity = 155 + int(100 * abs(self.neon_phase) // 100)
            intensity = max(0, min(255, intensity))
            color = f"#{intensity:02x}ffff"
            self.jarvis_text.configure(fg=color)

            self.neon_phase += self.neon_direction * 5
            if self.neon_phase >= 100 or self.neon_phase <= 0:
                self.neon_direction *= -1

            self.root.after(100, update_color)

        update_color()