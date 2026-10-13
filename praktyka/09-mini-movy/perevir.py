"""Перевіряє mini-languages.py на тестовій теці з відомими файлами.

Запуск (з кореня репозиторію):
    python praktyka/09-mini-movy/perevir.py

Створює тимчасову теку з 14 файлами (розміри й дати зміни відомі заздалегідь),
запускає ваш скрипт на ній і перевіряє кожну з пʼяти міні-мов окремо.
"""
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

TUT = Path(__file__).resolve().parent
SKRYPT = TUT / "mini-languages.py"

# імʼя, розмір у байтах, дата зміни
FAYLY = [
    ("zvit_2026-10-01.pdf", 51200, "2026-10-01"),
    ("foto_2026-09-15.jpg", 46592, "2026-09-15"),
    ("prezentatsiya.pptx", 40448, "2026-10-03"),
    ("kopiya_2025-12-31.zip", 33280, "2025-12-31"),
    ("rozklad_2026-9-1.txt", 28160, "2026-09-01"),
    ("tablytsia.xlsx", 22630, "2026-08-20"),
    ("2026-11-09.md", 17510, "2026-11-09"),
    ("dyplom.docx", 12390, "2026-06-30"),
    ("versiya_1.2.3.txt", 9318, "2026-10-05"),
    ("logo.png", 5120, "2026-02-14"),
    ("notatky.txt", 2560, "2026-10-07"),
    ("log_2026-10-20.txt", 1536, "2026-10-20"),
    ("todo.md", 700, "2026-10-08"),
    ("pusto.txt", 0, "2026-10-09"),
]
TEKA = "arhiv_2026-01-01"          # підтека: у звіт потрапити не має
Z_DATOYU = 5                        # zvit, foto, kopiya, 2026-11-09, log — rozklad_2026-9-1 НЕ рахується


def stvoryty(papka):
    for imia, rozmir, data in FAYLY:
        f = Path(papka) / imia
        f.write_bytes(b"x" * rozmir)
        chas = datetime.strptime(data + " 12:00", "%Y-%m-%d %H:%M").timestamp()
        os.utime(f, (chas, chas))
    (Path(papka) / TEKA).mkdir()


def zapustyty(papka):
    try:
        r = subprocess.run([sys.executable, str(SKRYPT), papka], capture_output=True,
                           text=True, encoding="utf-8", timeout=30,
                           env={**os.environ, "PYTHONUTF8": "1"})
    except subprocess.TimeoutExpired:
        return None, "скрипт працює понад 30 секунд"
    if r.returncode != 0:
        return None, r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "скрипт завершився з помилкою"
    return r.stdout, None


def poyasnyty_pomylku(pomylka):
    if "Invalid format specifier" in pomylka or "Unknown format code" in pomylka:
        return "у f-рядку таблиці лишилось «...» або неправильна специфікація — крок 3, мова 3"
    if "slice indices" in pomylka or "list indices" in pomylka or "ellipsis" in pomylka.lower():
        return "у зрізі лишилось «...» — потрібно [початок:кінець]"
    if "re.error" in pomylka or "PatternError" in pomylka or "nothing to repeat" in pomylka:
        return "регулярний вираз не компілюється — крок 3, мова 5"
    return ""


def main():
    if not SKRYPT.exists():
        sys.exit(f"Не знайдено {SKRYPT}. Візьміть його з шаблону (крок 0 інструкції).")
    with tempfile.TemporaryDirectory() as papka:
        stvoryty(papka)
        vyvid, pomylka = zapustyty(papka)
    if pomylka:
        print(f"❌ Скрипт не запустився: {pomylka}")
        p = poyasnyty_pomylku(pomylka)
        if p:
            print(f"   ← {p}")
        return
    ryadky = vyvid.splitlines()
    print("Ваш скрипт вивів:\n")
    print("\n".join("   " + r for r in ryadky))
    print()

    ochikuvani = sorted(FAYLY, key=lambda f: f[1], reverse=True)
    top, reshta = ochikuvani[:10], ochikuvani[10:]
    zaraz = 0

    def ryadok_z(imia):
        return next((r for r in ryadky if imia in r), None)

    # 1. glob
    znaideni = [f for f in FAYLY if ryadok_z(f[0])]
    if not znaideni:
        print("❌ 1. glob: у таблиці немає жодного файлу — шаблон має брати все: \"*\"")
    else:
        print("✅ 1. glob: файли знайдено")
        zaraz += 1
    if any(TEKA in r for r in ryadky):
        print(f"   ⚠️ у таблиці є підтека {TEKA} — фільтр os.path.isfile прибрали?")

    # 2. зріз і порядок
    zayvi = [f[0] for f in reshta if ryadok_z(f[0])]
    poriadok = [i for i, r in enumerate(ryadky) for f in top if f[0] in r]
    if not znaideni:
        print("⏳ 2. зріз: спершу glob")
    elif zayvi:
        print(f"❌ 2. зріз: у таблиці зайві файли ({', '.join(zayvi)}) — лише 10 найбільших: [:10]")
    elif len([f for f in top if ryadok_z(f[0])]) < 10:
        print("❌ 2. зріз: у таблиці менше 10 файлів — [:10], а не менше")
    elif poriadok != sorted(poriadok):
        print("❌ 2. зріз: файли не від найбільшого — сортування reverse=True вже є, не змінюйте його")
    else:
        print("✅ 2. зріз: рівно 10 найбільших, від найбільшого")
        zaraz += 1

    # 3. формат рядків: КБ з одним знаком і вирівнювання праворуч
    if znaideni:
        dobri, kintsi = 0, set()
        for imia, rozmir, _ in top:
            r = ryadok_z(imia)
            if not r:
                continue
            kb = f"{rozmir / 1024:.1f}"
            m = re.search(r"(?<![\d.])" + re.escape(kb) + r"(?![\d])", r)
            if m:
                dobri += 1
                kintsi.add(m.end())
        if dobri < len([f for f in top if ryadok_z(f[0])]):
            print("❌ 3. формат: розмір не в КБ з одним знаком після коми — специфікація на кшталт >8.1f")
        elif len(kintsi) > 1:
            print("❌ 3. формат: стовпець КБ не вирівняний — імʼя в полі фіксованої ширини (<30), КБ праворуч (>8)")
        else:
            print("✅ 3. формат: КБ з одним знаком, стовпці рівні")
            zaraz += 1
    else:
        print("⏳ 3. формат: спершу glob")

    # 4. формат дати
    if znaideni:
        imia, _, data = top[0]
        r = ryadok_z(imia).replace(imia, "")
        pravylno = datetime.strptime(data, "%Y-%m-%d").strftime("%d.%m.%Y")
        if pravylno in r:
            print("✅ 4. дата: дд.мм.рррр")
            zaraz += 1
        elif data in r:
            print("❌ 4. дата: вийшло рррр-мм-дд — порядок кодів %d.%m.%Y")
        elif datetime.strptime(data, "%Y-%m-%d").strftime("%d.%m.%y") in r:
            print("❌ 4. дата: рік двома цифрами — %Y велика, не %y")
        else:
            print(f"❌ 4. дата: для {imia} очікувалось {pravylno}")
    else:
        print("⏳ 4. дата: спершу glob")

    # 5. регулярний вираз
    m = next((re.search(r"(\d+)\s*$", r) for r in ryadky if "дат" in r.lower() and re.search(r"\d+\s*$", r)), None)
    if not m:
        print("❌ 5. регулярка: не знайдено рядок «З датою в назві: N»")
    else:
        n = int(m.group(1))
        if n == Z_DATOYU:
            print(f"✅ 5. регулярка: з датою в назві — {Z_DATOYU}")
            zaraz += 1
        elif n == Z_DATOYU + 1:
            print("❌ 5. регулярка: вийшло 6 — вираз пропустив rozklad_2026-9-1.txt; рррр-мм-дд — це рівно 4, 2 і 2 цифри")
        elif n == Z_DATOYU - 1:
            print("❌ 5. регулярка: вийшло 4 — рахуйте серед УСІХ файлів (fayly), а не лише топ-10")
        elif n == 0:
            print("❌ 5. регулярка: нуль — у виразі лишилось «...»?")
        elif n >= len(FAYLY) - 2:
            print("❌ 5. регулярка: майже всі файли — вираз надто загальний; потрібні цифри й дефіси: \\d{4}-...")
        else:
            print(f"❌ 5. регулярка: вийшло {n}, а має бути {Z_DATOYU}")

    print(f"\nРазом: {zaraz} з 5 міні-мов ✅   (мінімум для зарахування — 4 з 5)")


if __name__ == "__main__":
    main()
