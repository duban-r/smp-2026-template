"""Перевіряє ваші регулярні вирази з vyrazy.py на готових прикладах.

Запуск (з кореня репозиторію):
    python praktyka/05-regex/perevir.py

Для пунктів 1–5 вираз шукається в рядку через re.search — тобто так само,
як на regex101. Якщо забули якорі ^ і $, вираз знайде шматок усередині
«чужого» рядка, і тест це покаже.
Для пункту 6 перевіряється re.findall на готовому тексті.
"""
import importlib.util
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

TUT = Path(__file__).parent

# ключ: (назва, мають збігтися, НЕ мають збігтися)
TESTY = {
    "chas": (
        "1. Час ГГ:ХХ від 00:00 до 23:59",
        ["00:00", "09:05", "12:30", "23:59"],
        ["24:00", "23:60", "9:05", "12.30", "123:45", "почало о 12:30"],
    ),
    "data": (
        "2. Дата дд.мм.рррр, місяць від 01 до 12",
        ["25.07.2026", "01.12.1999", "31.01.2026"],
        ["25.13.2026", "25.00.2026", "5.07.2026", "25/07/2026", "25.07.26", "дата 25.07.2026"],
    ),
    "ip": (
        "3. IP-адреса: чотири числа по 1–3 цифри через крапку",
        ["192.168.10.15", "10.0.0.7", "8.8.8.8"],
        ["192.168.10", "192.168.10.15.1", "192,168,10,15", "1921.168.10.15", "IP 10.0.0.7"],
    ),
    "identyfikator": (
        "4. Імʼя змінної Python: латинська літера або _, далі літери, цифри, _",
        ["x", "_temp", "total_2", "MAX_SIZE"],
        ["2total", "total-2", "my var", "x!", ""],
    ),
    "velyki": (
        "5. Лише великі латинські літери, від 3 до 8",
        ["ABC", "UKRAINE", "ABCDEFGH"],
        ["AB", "ABCDEFGHI", "Abc", "АБВ", "AB1", "ABC DEF"],
    ),
}

TEKST = ("Регулярні вирази допомагають автоматизувати перевірку конфігурацій, "
         "а не лише шукати слова.")
DOVGI = ["Регулярні", "допомагають", "автоматизувати", "перевірку", "конфігурацій"]

ZIRKA = {
    "data_povna": (
        "⭐ Дата з перевіркою днів у місяці (29.02 — завжди можна)",
        ["31.01.2026", "30.04.2026", "29.02.2024", "31.12.2026"],
        ["31.04.2026", "30.02.2026", "32.01.2026", "00.01.2026", "31.11.2026"],
    ),
    "ip_0_255": (
        "⭐ IP-адреса, кожне число від 0 до 255",
        ["255.255.255.0", "0.0.0.0", "192.168.10.15"],
        ["256.1.1.1", "999.999.999.999", "01.02.03.004", "192.168.10"],
    ),
    "nomer_avto": (
        "⭐ Український номерний знак: АА1234ВВ, лише літери, схожі на латинські",
        ["АА1234ВВ", "КА0001ХР"],
        ["AA1234BB", "АА123ВВ", "ЯЯ1234ЯЯ", "аа1234вв", "АА 1234 ВВ"],
    ),
}

PIDKAZKY = {
    "почало о 12:30": "вираз знайшов шматок усередині — забули якорі ^ і $",
    "дата 25.07.2026": "вираз знайшов шматок усередині — забули якорі ^ і $",
    "IP 10.0.0.7": "вираз знайшов шматок усередині — забули якорі ^ і $",
    "ABCDEFGHI": "без якорів ^ і $ вираз знайде 8 літер усередині 9",
    "25/07/2026": "крапка без \\ означає «будь-який символ»: пишіть \\.",
    "192,168,10,15": "крапка без \\ означає «будь-який символ»: пишіть \\.",
    "24:00": "години 20–23 — окремий випадок: після 2 може бути лише 0–3",
    "23:60": "хвилини: перша цифра лише 0–5",
    "25.13.2026": "місяць: або 0 і цифра 1–9, або 1 і цифра 0–2",
    "25.00.2026": "місяць 00 не буває",
    "АБВ": "це кирилиця: [A-Z] — лише латиниця, а \\w бере будь-які літери",
    "2total": "імʼя не може починатися з цифри",
    "": "порожній рядок не є імʼям: після першого символу може бути *, але сам перший — обовʼязковий",
    "AA1234BB": "це латинські A і B — на номерах кирилиця",
}


def zavantazhyty():
    shliakh = TUT / "vyrazy.py"
    if not shliakh.exists():
        sys.exit(f"Не знайдено {shliakh}. Візьміть його з шаблону (крок 0 інструкції).")
    spec = importlib.util.spec_from_file_location("vyrazy", shliakh)
    modul = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(modul)
    except SyntaxError as e:
        sys.exit(f"У vyrazy.py синтаксична помилка, рядок {e.lineno}: {e.msg}\n"
                 f"Найчастіше — забута лапка або кома після r\"...\".")
    return getattr(modul, "VYRAZY", {})


def skompiliuvaty(vyraz):
    try:
        return re.compile(vyraz), None
    except re.error as e:
        return None, f"вираз не компілюється: {e}"


def perevirka(kliuch, nazva, tak, ni, vyrazy):
    print(f"\n== {nazva}")
    vyraz = vyrazy.get(kliuch, "")
    if not vyraz:
        print("  ⏳ ще не заповнено")
        return None
    shablon, pomylka = skompiliuvaty(vyraz)
    if pomylka:
        print(f"  ❌ {pomylka}")
        return False
    provaly = []
    for s in tak:
        if not shablon.search(s):
            provaly.append(f"мав збігтися, але ні:        {s!r}")
    for s in ni:
        if shablon.search(s):
            pidkazka = PIDKAZKY.get(s)
            provaly.append(f"НЕ мав збігтися, але збігся: {s!r}" + (f"  ← {pidkazka}" if pidkazka else ""))
    vsogo = len(tak) + len(ni)
    if provaly:
        print(f"  ❌ {vsogo - len(provaly)}/{vsogo}")
        for p in provaly:
            print("     " + p)
        return False
    print(f"  ✅ {vsogo}/{vsogo}")
    return True


def main():
    vyrazy = zavantazhyty()
    rezultaty = [perevirka(k, *TESTY[k], vyrazy) for k in TESTY]

    print("\n== 6. Усі слова, довші за 8 літер (re.findall на тексті)")
    vyraz = vyrazy.get("dovgi_slova", "")
    if not vyraz:
        print("  ⏳ ще не заповнено")
        rezultaty.append(None)
    else:
        shablon, pomylka = skompiliuvaty(vyraz)
        if pomylka:
            print(f"  ❌ {pomylka}")
            rezultaty.append(False)
        else:
            znaideno = shablon.findall(TEKST)
            if znaideno == DOVGI:
                print(f"  ✅ знайдено рівно {len(DOVGI)} слів")
                rezultaty.append(True)
            else:
                print(f"  ❌ очікувалось: {DOVGI}")
                print(f"     знайдено:    {znaideno}")
                if znaideno and isinstance(znaideno[0], tuple):
                    print("     ← у виразі є група ( ), і findall повертає групи; зробіть її (?: ) або приберіть")
                rezultaty.append(False)

    zirky = {k: v for k, v in ZIRKA.items() if vyrazy.get(k)}
    for k, v in zirky.items():
        perevirka(k, *v, vyrazy)

    gotovo = sum(1 for r in rezultaty if r)
    print(f"\nРазом: {gotovo} з 6 пунктів повністю ✅")
    if not zirky:
        print("⭐ Хочете більше? Додайте у VYRAZY ключі data_povna, ip_0_255 або nomer_avto.")


if __name__ == "__main__":
    main()
