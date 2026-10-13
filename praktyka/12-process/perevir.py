"""Перевіряє process.md — формалізацію вашого процесу.

Запуск (з кореня репозиторію):
    python praktyka/12-process/perevir.py

Дивиться на пʼять розділів: опис, учасники, правила When / If / Then, схема mermaid,
SQL і регулярні вирази. Перевіряє форму, а не зміст: чи правило справді має подію
й дію, чи схема має розгалуження. Чи правила розумні — вирішуємо на розборі.
"""
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

FAIL = Path(__file__).resolve().parent / "process.md"
ZAGLUSHKA = "…"

WHEN = re.compile(r"^\s*(when|коли)\b\s*(.*)$", re.I)
IF = re.compile(r"^\s*(if|якщо)\b\s*(.*)$", re.I)
THEN = re.compile(r"^\s*(then|то|тоді)\b\s*(.*)$", re.I)


def rozdily(tekst):
    chastyny = re.split(r"^##\s+(.+)$", tekst, flags=re.M)
    return {nazva.strip().lower(): vmist for nazva, vmist in zip(chastyny[1::2], chastyny[2::2])}


def znaity(rozd, *slova):
    for nazva, vmist in rozd.items():
        if any(s in nazva for s in slova):
            return vmist
    return None


def pravyla(tekst):
    bloky, potochnyi = [], None
    for ryadok in tekst.splitlines():
        if (m := WHEN.match(ryadok)):
            potochnyi = {"when": m.group(2).strip(), "if": None, "then": None}
            bloky.append(potochnyi)
        elif potochnyi is not None:
            if (m := IF.match(ryadok)) and potochnyi["if"] is None:
                potochnyi["if"] = m.group(2).strip()
            elif (m := THEN.match(ryadok)) and potochnyi["then"] is None:
                potochnyi["then"] = m.group(2).strip()
    return bloky


def zapovneno(s):
    return bool(s) and ZAGLUSHKA not in s and len(s.strip()) > 2


def main():
    if not FAIL.exists():
        sys.exit(f"Не знайдено {FAIL}. Візьміть заготовку з шаблону (крок 0 інструкції).")
    tekst = FAIL.read_text(encoding="utf-8")
    rozd = rozdily(tekst)
    zaraz, holovne = 0, 0

    # 1. опис
    opys = znaity(rozd, "опис")
    if opys is None:
        print("❌ 1. немає розділу «## Опис»")
    else:
        chysti = re.sub(r"<!--.*?-->", "", opys, flags=re.S)
        rechennia = [r for r in re.split(r"[.!?]+", chysti) if len(r.split()) >= 3 and ZAGLUSHKA not in r]
        if len(rechennia) >= 5:
            print(f"✅ 1. опис — {len(rechennia)} речень")
            zaraz += 1
        else:
            print(f"❌ 1. в описі {len(rechennia)} повноцінних речень, а треба 5–8")

    # 2. учасники
    uchasnyky = znaity(rozd, "учасник")
    punkty = [r for r in (uchasnyky or "").splitlines() if r.strip().startswith(("-", "*")) and zapovneno(r)]
    if len(punkty) >= 2:
        print(f"✅ 2. учасників — {len(punkty)}")
        zaraz += 1
    else:
        print(f"❌ 2. учасників {len(punkty)} — щонайменше два пункти списку «- хто — що робить»")

    # 3. правила
    vsi = pravyla(znaity(rozd, "правил") or "")
    dobri = [p for p in vsi if zapovneno(p["when"]) and zapovneno(p["then"])]
    z_umovoiu = [p for p in dobri if zapovneno(p["if"])]
    bez_then = [p for p in vsi if zapovneno(p["when"]) and not zapovneno(p["then"])]
    if len(dobri) >= 5 and len(z_umovoiu) >= 3:
        print(f"✅ 3. правил — {len(dobri)}, з умовою If — {len(z_umovoiu)}")
        zaraz += 1
        holovne += 1
    else:
        print(f"❌ 3. повних правил (When + Then) — {len(dobri)}, з них з умовою If — {len(z_umovoiu)}; "
              "треба щонайменше 5 правил, з них 3 з умовою")
        if bez_then:
            print(f"     ← у {len(bez_then)} правил є When, але немає Then: що саме має статися?")
        if not vsi:
            print("     ← кожне правило починається рядком «When …» (або «Коли …») у розділі «## Правила»")

    # 4. схема
    blok = re.search(r"```mermaid\s*\n(.*?)```", znaity(rozd, "схем") or "", flags=re.S)
    if not blok:
        print("❌ 4. у розділі «## Схема» немає блоку ```mermaid")
    else:
        kod = blok.group(1)
        vuzly = set(re.findall(r"\b([A-Za-z]\w*)\s*[\[\{\(]", kod))
        rishennia = re.findall(r"\{[^}]+\}", kod)
        mitky = re.findall(r"-->\s*\|[^|]+\|", kod)
        shablon = "Дія 1" in kod and "Дія 2" in kod
        if shablon:
            print("❌ 4. схема — ще шаблон із заготовки: намалюйте свій процес")
        elif not re.match(r"\s*(graph|flowchart)\s+(TD|TB|LR|RL|BT)", kod):
            print("❌ 4. схема має починатися з «graph TD» (або flowchart LR тощо)")
        elif len(vuzly) < 5 or not rishennia or len(mitky) < 2:
            print(f"❌ 4. у схемі вузлів {len(vuzly)}, умов {{…}} — {len(rishennia)}, підписаних стрілок — {len(mitky)}; "
                  "треба ≥ 5 вузлів, хоча б одна умова й дві підписані гілки -->|так| / -->|ні|")
        else:
            print(f"✅ 4. схема: вузлів {len(vuzly)}, умов {len(rishennia)}, підписаних гілок {len(mitky)}")
            zaraz += 1
            holovne += 1

    # 5. SQL і регулярки
    mova = znaity(rozd, "sql", "регуляр") or ""
    sql = any("sql" in r.lower() and zapovneno(r.split(":", 1)[-1]) and len(r) > 15 for r in mova.splitlines())
    regex = any(("регуляр" in r.lower() or "regex" in r.lower()) and zapovneno(r.split(":", 1)[-1]) and len(r) > 25
                for r in mova.splitlines())
    if sql and regex:
        print("✅ 5. є місця для SQL і для регулярного виразу")
        zaraz += 1
    else:
        brak = [n for n, ok in (("SQL", sql), ("регулярного виразу", regex)) if not ok]
        print(f"❌ 5. не заповнено: {', '.join(brak)} — рядок «SQL: де саме й навіщо»")

    print(f"\nРазом: {zaraz} з 5 ✅   (мінімум для зарахування — правила й схема, тобто 3 і 4)"
          + ("   ✔ мінімум є" if holovne == 2 else ""))


if __name__ == "__main__":
    main()
