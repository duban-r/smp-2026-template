"""Робота 7, крок 4: той самий пункт 4 — циклом на Python.

    python praktyka/07-sql/tsykl.py

Програма вже читає ВСІХ клієнтів. Ваше завдання — дописати цикл,
який залишить лише клієнтів з Польщі або Чехії й відсортує їх за прізвищем.
SQL тут лише «дай усе» — фільтр і сортування робите ви, як у роботі 6.
"""
import sqlite3
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

BAZA = Path(__file__).resolve().parents[2] / "data" / "chinook.db"
con = sqlite3.connect(BAZA)
klienty = con.execute("SELECT FirstName, LastName, Country FROM Customer").fetchall()
print(f"Усього клієнтів: {len(klienty)}")

vybrani = []
for imia, prizvyshche, krayina in klienty:
    ...  # ← ваш код: умова й append

# ← ваш код: сортування за прізвищем

for k in vybrani:
    print(*k)
