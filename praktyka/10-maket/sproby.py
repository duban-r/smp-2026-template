"""Робота 10, крок 1: перевірка передбачень.

Запускайте ТІЛЬКИ після того, як записали передбачення в peredbachennia.md:
    python praktyka/10-maket/sproby.py

Кожна спроба на мить відкриває маленьке вікно, вимірює, де стали написи, і закриває його.
"""
import sys
import tkinter as tk

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


def de(korin, *vidzhety):
    korin.update()
    return [(v.cget("text"), v.winfo_rootx() - korin.winfo_rootx(), v.winfo_rooty() - korin.winfo_rooty())
            for v in vidzhety]


def a():
    k = tk.Tk()
    ws = [tk.Label(k, text=t, bg="khaki") for t in ("A", "B", "C")]
    for w in ws:
        w.pack(side="left")
    r = de(k, *ws)
    k.destroy()
    return r


def b():
    k = tk.Tk()
    p = tk.Label(k, text="перший", bg="khaki")
    p.grid(row=0, column=0)
    d = tk.Label(k, text="у column=5", bg="khaki")
    d.grid(row=0, column=5)
    r = de(k, p, d)
    k.destroy()
    return r


def c():
    k = tk.Tk()
    k.geometry("300x200")
    w = tk.Label(k, text="центр?", bg="khaki")
    w.place(relx=0.5, rely=0.5)
    r = de(k, w) + [("середина вікна", 150, 100)]
    k.destroy()
    return r


def d():
    k = tk.Tk()
    p = tk.Entry(k)
    p.grid(row=0, column=0, sticky="ew")
    k.update()
    do = p.winfo_width()
    k.geometry(f"{k.winfo_width() + 200}x{k.winfo_height()}")
    k.update()
    r = [("ширина поля до", do, ""), ("після +200 px вікна", p.winfo_width(), "")]
    k.destroy()
    return r


def e():
    k = tk.Tk()
    ws = [tk.Label(k, text=t, bg="khaki") for t in ("1-top", "2-left", "3-top")]
    ws[0].pack(side="top")
    ws[1].pack(side="left")
    ws[2].pack(side="top")
    r = de(k, *ws)
    k.destroy()
    return r


SPROBY = [
    ("A", 'три написи: .pack(side="left") кожному', a),
    ("B", "один напис у column=0, другий у column=5 — стовпці 1–4 порожні", b),
    ("C", "вікно 300x200, напис .place(relx=0.5, rely=0.5) без anchor", c),
    ("D", 'поле .grid(sticky="ew") без columnconfigure — вікно ширшає на 200 px', d),
    ("E", 'pack: 1-й side="top", 2-й side="left", 3-й side="top"', e),
]

for bukva, opys, f in SPROBY:
    print(f"{bukva}  {opys}")
    for tekst, x, y in f():
        print(f"     {tekst:<22} {x} px" if y == "" else f"     {tekst:<22} x={x:<5} y={y}")
    print()
print("x, y — лівий верхній кут напису від лівого верхнього кута вікна, у пікселях.")
