"""Робота 11: заготовка калькулятора. Скопіюйте у kalkulyator.py і працюйте там:
    copy praktyka\11-podii\zahotovka_kalkulyator.py praktyka\11-podii\kalkulyator.py

Макет (тема 10) уже готовий. Ваше завдання — ПОВЕДІНКА: функції й звʼязування подій.
Перевірка:  python praktyka/11-podii/perevir.py
"""
import tkinter as tk

vikno = tk.Tk()
vikno.title("Калькулятор")

tk.Label(vikno, text="Перше:").grid(row=0, column=0, sticky="e", padx=8, pady=4)
pole_a = tk.Entry(vikno, width=14)
pole_a.grid(row=0, column=1, padx=8)

tk.Label(vikno, text="Друге:").grid(row=1, column=0, sticky="e", padx=8, pady=4)
pole_b = tk.Entry(vikno, width=14)
pole_b.grid(row=1, column=1, padx=8)

operatsiia = tk.StringVar(value="+")
ramka = tk.Frame(vikno)
ramka.grid(row=2, column=0, columnspan=2)
for znak in ("+", "−", "×", "÷"):
    tk.Radiobutton(ramka, text=znak, variable=operatsiia, value=znak).pack(side="left", padx=4)

rezultat = tk.Label(vikno, text="—", font=("Segoe UI", 16, "bold"))
rezultat.grid(row=4, column=0, columnspan=2, pady=6)


def porakhuvaty(podiia=None):
    ...  # ← прочитати два числа, порахувати, показати в rezultat; на «abc» — не падати


def ochystyty(podiia=None):
    ...  # ← очистити обидва поля й результат


tk.Button(vikno, text="Порахувати").grid(row=3, column=0, columnspan=2, pady=4)   # ← command=…

# ← звʼязування подій: Enter у полях, Esc у вікні

vikno.mainloop()
