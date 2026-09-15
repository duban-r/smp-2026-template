"""Робота 6, крок 2: перевірка передбачень.

Запускайте ТІЛЬКИ після того, як записали передбачення в peredbachennia.md:
    python praktyka/06-regex-log/sproby.py
"""
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

zhurnal = Path(__file__).parents[2] / "data" / "access.log"
ryadok = zhurnal.read_text(encoding="utf-8").splitlines()[0]

print("Рядок журналу:")
print(" ", ryadok)
print()
print("A  re.search(r'\"(.*)\"', ryadok).group(1)")
print("  →", repr(re.search(r'"(.*)"', ryadok).group(1)))
print()
print("B  re.search(r'\"(.*?)\"', ryadok).group(1)")
print("  →", repr(re.search(r'"(.*?)"', ryadok).group(1)))
print()
print("C  re.search(r'(\\d{3}) (\\d+)', ryadok).groups()")
print("  →", re.search(r"(\d{3}) (\d+)", ryadok).groups())
print()
print("D  re.findall(r'\\d+\\.\\d+\\.\\d+\\.\\d+', ryadok)")
print("  →", re.findall(r"\d+\.\d+\.\d+\.\d+", ryadok))
print()
print("E  re.sub(r'(\\d+)/(\\w+)/(\\d+)', r'\\3-\\2-\\1', '17/Mar/2026')")
print("  →", repr(re.sub(r"(\d+)/(\w+)/(\d+)", r"\3-\2-\1", "17/Mar/2026")))
