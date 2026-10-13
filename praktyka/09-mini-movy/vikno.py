"""Робота 9, крок 1: перше вікно Tkinter.

    python praktyka/09-mini-movy/vikno.py

Допишіть: у заголовку вікна — сьогоднішня дата (формат дати),
у написі — ваше імʼя по центру поля з 20 зірочок (формат рядків).
"""
import tkinter as tk
from datetime import datetime

vikno = tk.Tk()
vikno.title("Робота 9")                 # ← сюди дату: f"Робота 9 · {datetime.now():...}"
vikno.geometry("320x140")               # ширина x висота — ще одна міні-мова

napys = "Ваше Імʼя"                     # ← f"{'Ваше Імʼя':...}"
tk.Label(vikno, text=napys, font=("Consolas", 14)).pack(pady=20)
tk.Button(vikno, text="Закрити", command=vikno.destroy).pack()

vikno.mainloop()
