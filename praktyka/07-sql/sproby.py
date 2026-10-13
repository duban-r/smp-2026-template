"""Робота 7, крок 2: перевірка передбачень.

Запускайте ТІЛЬКИ після того, як записали передбачення в peredbachennia.md:
    python praktyka/07-sql/sproby.py
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

SPROBY = [
    ("A", "SELECT 7 / 2, 7 / 2.0"),
    ("B", "SELECT COUNT(*), COUNT(Composer) FROM Track"),
    ("C", "SELECT 'Abba' LIKE 'a%', 'Abba' = 'abba'"),
    ("D", "SELECT Composer FROM Track ORDER BY Composer LIMIT 1"),
    ("E", "SELECT NULL OR 1, NULL AND 1"),
]

for bukva, zapyt in SPROBY:
    ryadok = con.execute(zapyt).fetchone()
    pokaz = " | ".join("NULL" if v is None else str(v) for v in ryadok)
    print(f"{bukva}  {zapyt}\n   → {pokaz}\n")

print("1 у SQLite означає «істина», 0 — «хиба», NULL — «невідомо».")
