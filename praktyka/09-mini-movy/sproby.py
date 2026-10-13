"""Робота 9, крок 2: перевірка передбачень.

Запускайте ТІЛЬКИ після того, як записали передбачення в peredbachennia.md:
    python praktyka/09-mini-movy/sproby.py
"""
import sys
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

SPROBY = [
    ("A", 'f"{7:03}"', lambda: f"{7:03}"),
    ("B", "f\"[{'кіт':-<6}]\"", lambda: f"[{'кіт':-<6}]"),
    ("C", 'f"{2.5:.0f} {3.5:.0f}"', lambda: f"{2.5:.0f} {3.5:.0f}"),
    ("D", 'datetime(2026, 11, 9).strftime("%y/%m %A")', lambda: datetime(2026, 11, 9).strftime("%y/%m %A")),
    ("E", '"0123456789"[8:2:-2]', lambda: "0123456789"[8:2:-2]),
]

for bukva, kod, f in SPROBY:
    print(f"{bukva}  {kod}\n   → {f()!r}\n")
