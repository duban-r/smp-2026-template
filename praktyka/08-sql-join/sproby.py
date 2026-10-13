"""Робота 8, крок 2: перевірка передбачень.

Запускайте ТІЛЬКИ після того, як записали передбачення в peredbachennia.md:
    python praktyka/08-sql-join/sproby.py
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
    ("A", "SELECT COUNT(*) FROM Artist JOIN Album ON Artist.ArtistId = Album.ArtistId"),
    ("B", "SELECT COUNT(*) FROM Artist LEFT JOIN Album ON Artist.ArtistId = Album.ArtistId"),
    ("C", "SELECT COUNT(*) FROM Artist, Album"),
    ("D", "SELECT COUNT(*) FROM Track WHERE GenreId = 1 GROUP BY AlbumId"),
    ("E", "SELECT SUM(Total), COUNT(*) FROM Invoice WHERE BillingCountry = 'Ukraine'"),
]

print("Для порівняння: Artist — 275 рядків, Album — 347.\n")
for bukva, zapyt in SPROBY:
    ryadky = con.execute(zapyt).fetchall()
    pershyi = " | ".join("NULL" if v is None else str(v) for v in ryadky[0])
    print(f"{bukva}  {zapyt}")
    print(f"   → рядків у результаті: {len(ryadky)}; перший: {pershyi}\n")
