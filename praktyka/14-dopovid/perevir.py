"""Перевіряє роботу 14: відповіді в chytannia.md і чернетку dopovid.md.

Запуск (з кореня репозиторію):
    python praktyka/14-dopovid/perevir.py

Правильних відповідей тут немає — лише їхні відбитки, тож скрипт каже «так / ні»
і підказує, куди дивитись, але не відповідає за вас.
"""
import hashlib
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

TUT = Path(__file__).resolve().parent
ZAGLUSHKA = "…"

VIDBYTKY = {}       # номер → відбиток правильної літери
PIDKAZKY = {        # номер → підказка, якщо відповідь неправильна
    1: "дивіться на ключ on: — там дві події; cron 0 6 * * 1 — пʼятий стовпець це день тижня",
    2: "Actions лише виконує кроки й показує результат — нічого не відкочує",
    3: "Terraform — декларативна мова: опис того, ЩО має бути",
    4: "Terraform порівнює опис із фактичним станом і робить лише різницю",
    5: "Docker кешує кожен крок; кеш кроку ламається, коли змінились його вхідні файли",
    6: "RUN працює під час збирання, а CMD — команда за замовчуванням для запущеного контейнера",
    7: "кожен рядок сценарію має бути привʼязаний до коду; немає привʼязки — виконати нічого",
    8: "Припустимо — дані, Коли — дія, Тоді — …",
    9: "головна обіцянка GraphQL — усе потрібне одним запитом",
    10: "клієнт сам перелічує поля, які хоче отримати",
    11: "make порівнює час зміни цілі й джерела",
    12: "рядок «ціль: джерело» — це не крок, а залежність",
}


def vidbytok(n, bukva):
    return hashlib.sha256(f"smp-14:{n}:{bukva}".encode()).hexdigest()[:10]


VIDBYTKY.update({1: "b01ed34523", 2: "2cbd303fb0", 3: "bedecaee54", 4: "0126067293", 5: "6a96e9004c", 6: "0a6e829fc4", 7: "6a49dcee97", 8: "8973d24e13", 9: "a64012dd12", 10: "2b8684beeb", 11: "f0d6135452", 12: "38699c178d"})


def chytannia():
    fail = TUT / "chytannia.md"
    print("== chytannia.md — 12 питань")
    if not fail.exists():
        print("  ⏳ немає файлу — візьміть із шаблону (крок 0)")
        return 0, 0
    tekst = fail.read_text(encoding="utf-8").split("## Відповіді", 1)[-1]
    vidpovidi = {int(m.group(1)): (m.group(2).lower(), m.group(3).strip())
                 for m in re.finditer(r"^\s*(\d{1,2})\s*[:.)]\s*([abcdABCD])\b\s*[—–-]?\s*(.*)$", tekst, re.M)}
    pravylno = z_poyasnenniam = 0
    for n in range(1, 13):
        if n not in vidpovidi:
            print(f"  ⏳ {n}: немає відповіді")
            continue
        bukva, chomu = vidpovidi[n]
        if vidbytok(n, bukva) == VIDBYTKY[n]:
            pravylno += 1
            dobre_poyasnennia = len(chomu.split()) >= 3
            z_poyasnenniam += dobre_poyasnennia
            print(f"  ✅ {n}" + ("" if dobre_poyasnennia else "  ← допишіть одне речення «бо …»"))
        else:
            print(f"  ❌ {n}: {bukva} — ні. Підказка: {PIDKAZKY[n]}")
    print(f"  Разом: {pravylno} з 12 правильно, з поясненням — {z_poyasnenniam}")
    return pravylno, z_poyasnenniam


def rozdily(tekst):
    chastyny = re.split(r"^##\s+(.+)$", tekst, flags=re.M)
    return {n.strip().lower(): v for n, v in zip(chastyny[1::2], chastyny[2::2])}


def dopovid():
    fail = TUT / "dopovid.md"
    print("\n== dopovid.md — чернетка доповіді")
    if not fail.exists():
        print("  ⏳ немає файлу — візьміть із шаблону (крок 0)")
        return False
    tekst = re.sub(r"<!--.*?-->", "", fail.read_text(encoding="utf-8"), flags=re.S)
    zaholovok = re.search(r"^#\s+Доповідь:\s*(.+)$", tekst, re.M)
    rozd = rozdily(tekst)
    provaly = []
    if not zaholovok or ZAGLUSHKA in zaholovok.group(1):
        provaly.append("у заголовку немає назви мови: # Доповідь: Terraform")
    for kluch, nazva, minimum in (("задача", "Задача і користувач", 2), ("простим", "Що робить простим", 2),
                                  ("межа", "Межа", 2)):
        vmist = next((v for n, v in rozd.items() if kluch in n), "")
        rechennia = [r for r in re.split(r"[.!?]+", vmist) if len(r.split()) >= 3 and ZAGLUSHKA not in r]
        if len(rechennia) < minimum:
            provaly.append(f"розділ «{nazva}»: {len(rechennia)} речень, треба щонайменше {minimum}")
    pryklad = next((v for n, v in rozd.items() if "приклад" in n), "")
    blok = re.search(r"```[^\n]*\n(.*?)```", pryklad, re.S)
    ryadky = [r for r in (blok.group(1).splitlines() if blok else []) if r.strip()]
    if not blok or any(ZAGLUSHKA in r for r in ryadky):
        provaly.append("у розділі «Приклад» немає коду — блок ``` з прикладом мовою доповіді")
    elif not 5 <= len(ryadky) <= 15:
        provaly.append(f"приклад — {len(ryadky)} рядків, а для 5-хвилинної доповіді треба 5–15")
    dzherela = next((v for n, v in rozd.items() if "джерел" in n), "")
    if not re.search(r"https?://", dzherela):
        provaly.append("у «Джерелах» немає жодного посилання")
    if provaly:
        print("  ❌ зауваження:")
        for p in provaly:
            print(f"     · {p}")
        return False
    print(f"  ✅ чернетка повна: «{zaholovok.group(1).strip()}», приклад — {len(ryadky)} рядків")
    return True


def main():
    pravylno, _ = chytannia()
    dop = dopovid()
    print(f"\nМінімум для зарахування — 9 з 12 у chytannia.md і повна чернетка dopovid.md: "
          + ("✔ є" if pravylno >= 9 and dop else "ще ні"))


if __name__ == "__main__":
    main()
