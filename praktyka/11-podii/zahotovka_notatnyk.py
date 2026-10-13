"""Робота 11: заготовка нотатника. Скопіюйте у notatnyk.py і працюйте там:
    copy praktyka\11-podii\zahotovka_notatnyk.py praktyka\11-podii\notatnyk.py

Макет (тема 10) уже готовий. Ваше завдання — ПОВЕДІНКА: функції й звʼязування подій.
Перевірка:  python praktyka/11-podii/perevir.py
"""
import tkinter as tk

vikno = tk.Tk()
vikno.title("Нотатник")

verkh = tk.Frame(vikno)
verkh.pack(fill="x", padx=8, pady=6)
tk.Label(verkh, text="Файл:").pack(side="left")
pole_imeni = tk.Entry(verkh)
pole_imeni.pack(side="left", fill="x", expand=True, padx=6)
knopka = tk.Button(verkh, text="Зберегти")                       # ← command=…
knopka.pack(side="right")

tekst = tk.Text(vikno, width=60, height=15)
tekst.pack(fill="both", expand=True, padx=8)

status = tk.Label(vikno, text="Порожньо", fg="gray", anchor="w")
status.pack(fill="x", padx=8, pady=4)


def zberehty(podiia=None):
    ...  # ← записати текст у файл з імʼям із pole_imeni; без імені чи з помилкою — не падати


def ochystyty(podiia=None):
    ...  # ← очистити текст і імʼя файлу


# ← звʼязування подій: Enter у полі імені, Esc у вікні, Ctrl+S

vikno.mainloop()
