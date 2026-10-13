"""Робота 9: звіт про файли в теці — пʼять міні-мов усередині Python.

Запуск (з кореня репозиторію):
    python praktyka/09-mini-movy/mini-languages.py            — звіт про поточну теку
    python praktyka/09-mini-movy/mini-languages.py data       — звіт про теку data
Перевірка:
    python praktyka/09-mini-movy/perevir.py

Кожне місце з «...» — рядок або число на одній із пʼяти міні-мов. Замініть «...» своїм.
"""
import glob
import os
import re
import sys
from datetime import datetime

PAPKA = sys.argv[1] if len(sys.argv) > 1 else "."

# ── Мова 1: glob — шаблон імені файлу. Узяти ВСЕ, що є в теці ────────
elementy = glob.glob(os.path.join(PAPKA, "..."))
fayly = [f for f in elementy if os.path.isfile(f)]

# ── Мова 2: зріз — лише 10 найбільших ───────────────────────────────
fayly.sort(key=os.path.getsize, reverse=True)
top = fayly[...]

# ── Мова 3: формат рядків — таблиця. Заголовок уже готовий: ─────────
#    імʼя — ліворуч у полі 30, КБ — праворуч у полі 8, один знак після коми
print(f"{'Файл':<30}{'КБ':>8}  Змінено")
print("-" * 50)
for shliakh in top:
    imia = os.path.basename(shliakh)
    kb = os.path.getsize(shliakh) / 1024
    zmineno = datetime.fromtimestamp(os.path.getmtime(shliakh))

    # ── Мова 4: формат дати — дд.мм.рррр ────────────────────────────
    data = zmineno.strftime("...")

    print(f"{imia:...}{kb:...}  {data}")

# ── Мова 5: регулярний вираз — дата в назві файлу: рррр-мм-дд ───────
#    рахуємо серед УСІХ файлів теки, а не лише топ-10
DATA_V_NAZVI = re.compile(r"...")
z_datoyu = [f for f in fayly if DATA_V_NAZVI.search(os.path.basename(f))]
print("-" * 50)
print(f"Файлів у теці: {len(fayly)}")
print(f"З датою в назві: {len(z_datoyu)}")
