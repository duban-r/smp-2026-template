"""Робота 11, крок 1: перевірка передбачень.

Запускайте ТІЛЬКИ після того, як записали передбачення в peredbachennia.md:
    python praktyka/11-podii/sproby.py

Кожна спроба створює маленьке вікно, сама «натискає» кнопки й клавіші і записує, що сталося.
"""
import sys
import tkinter as tk

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

zhurnal = []


def nove():
    k = tk.Tk()
    k.report_callback_exception = lambda e, v, tb: zhurnal.append(f"помилка {e.__name__}: {v}")
    return k


def natysnuty(k, w, poslidovnist):
    w.focus_force(); k.update()
    w.event_generate(poslidovnist); k.update()


def a():
    k = nove()
    def pryvit():
        zhurnal.append("Привіт!")
    zhurnal.append("— створюю кнопку")
    b = tk.Button(k, text="OK", command=pryvit())
    zhurnal.append("— натискаю кнопку двічі")
    b.invoke(); b.invoke()
    k.destroy()


def b_():
    k = nove()
    knopky = [tk.Button(k, text=str(i), command=lambda: zhurnal.append(f"натиснуто {i}")) for i in range(3)]
    for kn in knopky:
        kn.invoke()
    k.destroy()


def c():
    k = nove()
    pole = tk.Entry(k); pole.pack()
    def porakhuvaty():
        zhurnal.append("порахували")
    pole.bind("<Return>", porakhuvaty)
    natysnuty(k, pole, "<Return>")
    k.destroy()


def d():
    k = nove()
    pole = tk.Entry(k); pole.pack()
    pole.bind("<Return>", lambda e: zhurnal.append("обробник поля"))
    k.bind("<Return>", lambda e: zhurnal.append("обробник вікна"))
    natysnuty(k, pole, "<Return>")
    k.destroy()


def e():
    k = nove()
    z = tk.StringVar(k)
    z.trace_add("write", lambda *a: zhurnal.append(f"зміна: {z.get()!r}"))
    z.set("кіт"); z.set("кіт"); z.set("")
    k.destroy()


SPROBY = [
    ("A", 'tk.Button(..., command=pryvit()) — потім кнопку натиснули двічі', a),
    ("B", "три кнопки в циклі: command=lambda: print(i) — натиснули кожну", b_),
    ("C", 'pole.bind("<Return>", porakhuvaty), де def porakhuvaty(): — без параметрів', c),
    ("D", "<Return> привʼязано і до поля, і до вікна — натиснули Enter у полі", d),
    ("E", 'trace_add("write") на StringVar, потім set("кіт"), set("кіт"), set("")', e),
]

for bukva, opys, f in SPROBY:
    zhurnal.clear()
    f()
    print(f"{bukva}  {opys}")
    for z in zhurnal or ["(нічого)"]:
        print(f"     {z}")
    print()
