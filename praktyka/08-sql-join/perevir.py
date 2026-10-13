"""Перевіряє ваші запити з sql-2.sql на базі data/chinook.db.

Запуск (з кореня репозиторію):
    python praktyka/08-sql-join/perevir.py        — усі пункти
    python praktyka/08-sql-join/perevir.py 3      — лише пункт 3, з усіма рядками результату

Для кожного пункту показує перші рядки результату й вердикт.
Правильних запитів тут немає — лише кількість рядків і «відбиток» правильної
відповіді, тож списати звідси не вийде, а перевірити себе — так.
"""
import hashlib
import re
import sqlite3
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

TUT = Path(__file__).resolve().parent
BAZA = TUT.parents[1] / "data" / "chinook.db"
FAIL = TUT / "sql-2.sql"

# пункт: опис, кількість рядків, стовпці-ключ, чи важливий порядок ключа,
#        (стовпець, напрям) для перевірки сортування, відбиток, підказки за кількістю рядків
PUNKTY = {
    1: dict(opys="Треки гурту Queen: трек, альбом",
            n=45, kluch=[0, 1], poriadok=False, sort=None, vidbytok="89e69f7a3496",
            pidkazky={3503: "усі треки магазину: де умова на виконавця?",
                      0: "нікого: виконавець записаний саме як 'Queen'; перевірте й умови ON",
                      963325: "мільйон рядків: у другому JOIN немає ON — кожен із кожним"}),
    2: dict(opys="Треків у кожному жанрі: жанр, кількість; від найбільшого",
            n=25, kluch=[0, 1], poriadok=False, sort=(1, "desc"), vidbytok="d7a4ccda7446",
            pidkazky={1: "один рядок: COUNT без GROUP BY згортає ВСЕ в одне число",
                      3503: "рядок на кожен трек: потрібне GROUP BY за жанром"}),
    3: dict(opys="Топ-10 клієнтів за сумою покупок: імʼя, прізвище, сума; від найбільшої",
            n=10, kluch=[0, 1], poriadok=False, sort=(-1, "desc"), vidbytok="638d871d0d38",
            pidkazky={1: "один рядок: потрібне GROUP BY за клієнтом",
                      59: "усі клієнти: LIMIT 10"}),
    4: dict(opys="Виконавці з більш ніж 5 альбомами: виконавець, альбомів; від найбільшого",
            n=6, kluch=[0, 1], poriadok=False, sort=(1, "desc"), vidbytok="750dc2f15cfd",
            pidkazky={204: "усі виконавці з альбомами: фільтр по кількості — HAVING після GROUP BY",
                      7: "«більш ніж 5» — це > 5, а не >= 5"}),
    5: dict(opys="Виконавці без жодного альбому",
            n=71, kluch=[0], poriadok=False, sort=None, vidbytok="993fafc3078d",
            pidkazky={0: "нікого: звичайний JOIN викидає тих, у кого немає пари. Потрібен LEFT JOIN",
                      275: "усі виконавці: після LEFT JOIN лишіть тих, у кого з боку Album порожньо (IS NULL)",
                      418: "LEFT JOIN є, але немає умови IS NULL"}),
    6: dict(opys="Середня тривалість треку по жанрах, хв з одним знаком; від найдовшої",
            n=25, kluch=[0], poriadok=False, sort=(1, "desc"), vidbytok="4ac75c41f8d2",
            pershyi=(1, 48.5, 0.051, "перший має бути ≈ 48.5 хвилини: AVG(Milliseconds) / 60000.0 і ROUND(…, 1)"),
            pidkazky={1: "один рядок: AVG без GROUP BY рахує середнє по всьому"}),
    7: dict(opys="Виторг за країнами (за рахунками): країна, сума; від найбільшого",
            n=24, kluch=[0], poriadok=False, sort=(1, "desc"), vidbytok="bb09d6874923",
            pershyi=(1, 523.06, 0.006, "перша — USA 523.06: SUM(Total) по країні, ROUND(…, 2)"),
            pidkazky={412: "рядок на кожен рахунок: GROUP BY за країною",
                      1: "один рядок: потрібне GROUP BY"}),
    8: dict(opys="Співробітники підтримки й кількість їхніх клієнтів; від найбільшого",
            n=3, kluch=[0, 1, 2], poriadok=False, sort=(-1, "desc"), vidbytok="af7dee0e3d04",
            pidkazky={59: "рядок на кожного клієнта: GROUP BY за співробітником",
                      0: "нікого: клієнт посилається на співробітника полем SupportRepId = EmployeeId",
                      8: "усі співробітники: звʼязок — Customer.SupportRepId = Employee.EmployeeId"}),
}


def vidbytok(ryadky, kluch, poriadok):
    """Короткий хеш ключових стовпців: однаковий лише для правильної відповіді."""
    kluchi = ["\x1f".join(str(r[i]).strip() for i in kluch) for r in ryadky]
    if not poriadok:
        kluchi.sort()
    return hashlib.sha256("\x1e".join(kluchi).encode("utf-8")).hexdigest()[:12]


def rozibraty(tekst):
    """Ділить sql-1.sql на пункти за рядками «-- 1.», «-- 2.» …"""
    chastyny = re.split(r"^--\s*(\d+)\.", tekst, flags=re.M)
    zapyty = {}
    for n, blok in zip(chastyny[1::2], chastyny[2::2]):
        bez = "\n".join(r for r in blok.splitlines()[1:] if not r.strip().startswith("--"))
        bez = bez.strip().rstrip(";").strip()
        zapyty[int(n)] = bez
    return zapyty


def vidsortovano(znachennia, napriam):
    para = list(zip(znachennia, znachennia[1:]))
    try:
        if napriam == "desc":
            return all(a >= b for a, b in para)
        return all(a <= b for a, b in para)
    except TypeError:
        return False


def pokazaty(kursor, ryadky, maks):
    nazvy = [d[0] for d in kursor.description]
    print("     " + " | ".join(nazvy))
    for r in ryadky[:maks]:
        print("     " + " | ".join("NULL" if v is None else str(v) for v in r))
    if len(ryadky) > maks:
        print(f"     … ще {len(ryadky) - maks}")


def perevirka(n, zapyt, con, maks):
    p = PUNKTY[n]
    print(f"\n== {n}. {p['opys']}")
    if not zapyt:
        print("  ⏳ ще не заповнено")
        return None
    if zapyt.count(";") > 0:
        print("  ❌ у пункті кілька запитів через «;» — лишіть один (решту закоментуйте --)")
        return False
    try:
        kursor = con.execute(zapyt)
        ryadky = kursor.fetchall()
    except sqlite3.Error as e:
        print(f"  ❌ SQLite: {e}")
        if "no such table" in str(e):
            print("     ← назви таблиць в однині з великої: Track, Album, Artist, Customer, Invoice")
        elif "no such column" in str(e):
            print("     ← подивіться стовпці: SELECT * FROM <таблиця> LIMIT 1")
        return False
    pokazaty(kursor, ryadky, maks)
    shyryna = max(p["kluch"]) + 1
    if ryadky and len(ryadky[0]) < shyryna:
        print(f"  ❌ замало стовпців — перечитайте, що саме показати")
        return False
    if len(ryadky) != p["n"]:
        print(f"  ❌ рядків {len(ryadky)}, а має бути {p['n']}")
        if len(ryadky) in p["pidkazky"]:
            print(f"     ← {p['pidkazky'][len(ryadky)]}")
        return False
    if vidbytok(ryadky, p["kluch"], p["poriadok"]) != p["vidbytok"]:
        if p["poriadok"] and vidbytok(ryadky, p["kluch"], False) == p.get("mnozhyna"):
            print("  ❌ рядки ті, але порядок не той — ORDER BY")
            return False
        print(f"  ❌ кількість правильна ({p['n']}), але рядки не ті"
              + (" або не в тому порядку" if p["poriadok"] else "")
              + " — перевірте умову й порядок стовпців")
        return False
    if p["sort"]:
        stovpets, napriam = p["sort"]
        if not vidsortovano([r[stovpets] for r in ryadky], napriam):
            slovo = "спадання" if napriam == "desc" else "зростання"
            print(f"  ❌ рядки ті, але не відсортовані за {slovo} — ORDER BY")
            return False
    if p.get("pershyi"):
        stovpets, znachennia, dopusk, pidkazka = p["pershyi"]
        try:
            dobre = abs(float(ryadky[0][stovpets]) - znachennia) <= dopusk
        except (TypeError, ValueError):
            dobre = False
        if not dobre:
            print(f"  ❌ рядки ті, але число не те — {pidkazka}")
            return False
    print(f"  ✅ правильно (рядків: {p['n']})")
    return True


def main():
    if not BAZA.exists():
        sys.exit(f"Не знайдено {BAZA}. Запускайте з кореня репозиторію; data/chinook.db є в шаблоні.")
    if not FAIL.exists():
        sys.exit(f"Не знайдено {FAIL}. Візьміть його з шаблону (крок 0 інструкції).")
    zapyty = rozibraty(FAIL.read_text(encoding="utf-8"))
    con = sqlite3.connect(f"file:{BAZA}?mode=ro", uri=True)
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
        perevirka(n, zapyty.get(n, ""), con, maks=10_000)
        return
    rezultaty = [perevirka(n, zapyty.get(n, ""), con, maks=3) for n in PUNKTY]
    gotovo = sum(1 for r in rezultaty if r)
    print(f"\nРазом: {gotovo} з {len(PUNKTY)} пунктів ✅   (мінімум для зарахування — пункти 1–5)")


if __name__ == "__main__":
    main()
