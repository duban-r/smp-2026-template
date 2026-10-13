"""Перевіряє ваші запити з sql-1.sql на базі data/chinook.db.

Запуск (з кореня репозиторію):
    python praktyka/07-sql/perevir.py        — усі пункти
    python praktyka/07-sql/perevir.py 3      — лише пункт 3, з усіма рядками результату

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
FAIL = TUT / "sql-1.sql"

# пункт: опис, кількість рядків, стовпці-ключ, чи важливий порядок ключа,
#        (стовпець, напрям) для перевірки сортування, відбиток, підказки за кількістю рядків
PUNKTY = {
    1: dict(opys="Треки, довші за 5 хвилин: назва, тривалість у секундах; від найдовшого",
            n=1069, kluch=[0], poriadok=False, sort=(1, "desc"),
            vidbytok="1e72fb744044",
            pidkazky={3503: "повернулись УСІ треки: Milliseconds — це мілісекунди, 5 хвилин = 300 000",
                      0: "жодного: перевірте одиниці — 5 хвилин у мілісекундах"}),
    2: dict(opys="Виконавці на A, за абеткою",
            n=26, kluch=[0], poriadok=True, sort=None,
            vidbytok="5a20950244ad", mnozhyna="5a20950244ad",
            pidkazky={275: "повернулись усі виконавці: де умова WHERE … LIKE?"}),
    3: dict(opys="Сім найдорожчих рахунків: номер, дата, країна, сума; від найбільшої",
            n=7, kluch=[0], poriadok=False, sort=(-1, "desc"),
            vidbytok="6614f66efd00",
            pidkazky={412: "повернулись усі рахунки: скільки рядків треба? — LIMIT",
                      10: "просили сім, а не десять"}),
    4: dict(opys="Клієнти з Польщі або Чехії: імʼя, прізвище, країна",
            n=3, kluch=[0, 1], poriadok=False, sort=None,
            vidbytok="0f5013ff11c6",
            pidkazky={1: "лише один: OR зʼєднує дві ПОВНІ умови — Country = '…' OR Country = '…'; або IN (…, …)",
                      2: "лише два: у базі країна записана як 'Czech Republic'",
                      0: "нікого: як саме записані країни? Подивіться SELECT DISTINCT Country FROM Customer"}),
    5: dict(opys="Приватні клієнти з Канади (Company порожнє): імʼя, прізвище, місто",
            n=6, kluch=[0, 1], poriadok=False, sort=None,
            vidbytok="9f451653a662",
            pidkazky={0: "нікого: з NULL не порівнюють через =, для цього є окремий оператор",
                      8: "усі канадці: умову на Company не застосовано",
                      49: "усі приватні клієнти: забули умову на країну"}),
    6: dict(opys="Країни клієнтів без повторів, за абеткою",
            n=24, kluch=[0], poriadok=True, sort=None,
            vidbytok="bb09d6874923", mnozhyna="bb09d6874923",
            pidkazky={59: "59 — це кількість клієнтів, а не країн: прибрати повтори"}),
    7: dict(opys="Альбоми зі словом Live у назві",
            n=17, kluch=[0], poriadok=False, sort=None,
            vidbytok="d9f366e3232d",
            pidkazky={0: "нікого: LIKE 'Live' шукає назву, рівну Live; для «містить» потрібні % з обох боків",
                      6: "лише ті, що ПОЧИНАЮТЬСЯ з Live: % потрібен і на початку"}),
    8: dict(opys="Рахунки за березень 2025: номер, дата, країна, сума; за датою",
            n=7, kluch=[0], poriadok=False, sort=(1, "asc"),
            vidbytok="d5855c60e594",
            pidkazky={5: "бракує двох — за 31 березня. Дата зберігається як '2025-03-31 00:00:00', "
                         "а цей текст «більший» за '2025-03-31'. Межа має бути інакшою"}),
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
    if n == 1 and ryadky and abs(ryadky[0][1] - 5286.953) > 1.5:
        print("  ❌ треки ті, але тривалість не в секундах: Milliseconds / 1000")
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
