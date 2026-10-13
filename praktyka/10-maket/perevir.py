"""Перевіряє три форми реєстрації: form_grid.py, form_pack.py, form_place.py.

Запуск (з кореня репозиторію):
    python praktyka/10-maket/perevir.py            — усі три
    python praktyka/10-maket/perevir.py grid       — лише одна

Кожну форму запускає окремо, на мить показує вікно, вимірює, де стоїть кожен
елемент, розтягує вікно — і закриває. Нічого у ваших файлах не змінює.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

TUT = Path(__file__).resolve().parent

# Код, який запускається замість mainloop(): описує вікно й одразу його закриває.
ZAMIST_MAINLOOP = r'''
import json, runpy, sys, tkinter as tk

def opysaty(korin):
    korin.update()
    x0, y0 = korin.winfo_rootx(), korin.winfo_rooty()
    vidzhety = []
    def obiity(w):
        for c in w.winfo_children():
            d = {"klas": c.winfo_class(), "menedzher": c.winfo_manager(),
                 "x": c.winfo_rootx() - x0, "y": c.winfo_rooty() - y0,
                 "w": c.winfo_width(), "h": c.winfo_height(), "tekst": "", "show": ""}
            for kluch in ("text", "show"):
                try:
                    d["tekst" if kluch == "text" else "show"] = str(c.cget(kluch))
                except tk.TclError:
                    pass
            vidzhety.append(d)
            obiity(c)
    obiity(korin)
    return {"W": korin.winfo_width(), "H": korin.winfo_height(), "vidzhety": vidzhety}

def zamist(self=None, n=0):
    korin = tk._default_root
    zvit = {"do": opysaty(korin)}
    korin.geometry(f"{korin.winfo_width() + 200}x{korin.winfo_height() + 120}")
    zvit["pislia"] = opysaty(korin)
    print("@@ZVIT@@" + json.dumps(zvit, ensure_ascii=False))
    korin.destroy()

tk.Misc.mainloop = zamist
tk.mainloop = zamist
runpy.run_path(sys.argv[1], run_name="__main__")
'''


def zapustyty(fail):
    try:
        r = subprocess.run([sys.executable, "-c", ZAMIST_MAINLOOP, str(fail)],
                           capture_output=True, text=True, encoding="utf-8", timeout=30,
                           env={**os.environ, "PYTHONUTF8": "1"})
    except subprocess.TimeoutExpired:
        return None, "форма не закрилась за 30 секунд — у файлі є щось, що чекає (input()?)"
    for ryadok in r.stdout.splitlines():
        if ryadok.startswith("@@ZVIT@@"):
            return json.loads(ryadok[8:]), None
    pomylka = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "у файлі немає vikno.mainloop()"
    return None, pomylka


def perevirka(menedzher):
    fail = TUT / f"form_{menedzher}.py"
    print(f"\n== form_{menedzher}.py")
    if not fail.exists():
        print("  ⏳ файлу немає — візьміть заготовку з шаблону (крок 0)")
        return None
    zvit, pomylka = zapustyty(fail)
    if pomylka:
        print(f"  ❌ не запустилась: {pomylka}")
        if "cannot use geometry manager" in pomylka:
            print("     ← два менеджери в ОДНОМУ контейнері. Один контейнер — один менеджер; інший — у вкладеній tk.Frame")
        return False

    do, pislia = zvit["do"], zvit["pislia"]
    v = do["vidzhety"]
    polia = [d for d in v if d["klas"] == "Entry"]
    pidpysy = [d for d in v if d["klas"] == "Label"]
    praporci = [d for d in v if d["klas"] == "Checkbutton"]
    knopky = [d for d in v if d["klas"] == "Button"]
    provaly = []

    if not any("Реєстрац" in d["tekst"] for d in pidpysy):
        provaly.append("немає заголовка з текстом «Реєстрація»")
    if len(polia) != 4:
        provaly.append(f"полів введення {len(polia)}, а має бути 4 (tk.Entry)")
    if polia and not any(d["show"] for d in polia):
        provaly.append('поле пароля показує символи — show="•"')
    if len(praporci) != 1:
        provaly.append(f"прапорців {len(praporci)}, а має бути 1 (tk.Checkbutton)")
    if not any("Зареєстр" in d["tekst"] for d in knopky) or not any("Скас" in d["tekst"] for d in knopky):
        provaly.append("потрібні дві кнопки: «Зареєструватись» і «Скасувати»")

    chuzhi = [d for d in polia + pidpysy if d["menedzher"] != menedzher]
    if chuzhi:
        inshi = sorted({d["menedzher"] or "жоден (забули розмістити?)" for d in chuzhi})
        provaly.append(f"підписи й поля мають стояти через {menedzher}, а тут: {', '.join(inshi)}")

    if len(polia) == 4 and not chuzhi:
        livi = [d["x"] for d in polia]
        if max(livi) - min(livi) > 3:
            pidk = {"pack": "у pack — однакова width у підписів, тоді поля стануть рівно",
                    "grid": "усі поля — в одному column",
                    "place": "однакове x у всіх полів"}[menedzher]
            provaly.append(f"поля не в одну колонку (ліві краї {sorted(livi)}) — {pidk}")
        bez_pidpysu = []
        for p in polia:
            tsentr = p["y"] + p["h"] / 2
            if not any(abs(l["y"] + l["h"] / 2 - tsentr) < 12 and l["x"] < p["x"] for l in pidpysy):
                bez_pidpysu.append(p)
        if bez_pidpysu:
            provaly.append(f"у {len(bez_pidpysu)} полів немає підпису ліворуч на тому самому рядку")

    if len(knopky) >= 2 and polia:
        nyz = max(d["y"] for d in polia + praporci)
        if min(d["y"] for d in knopky) <= nyz:
            provaly.append("кнопки мають бути нижче за поля й прапорець")
        if max(d["x"] + d["w"] for d in knopky) < do["W"] - 60:
            provaly.append("кнопки — праворуч: їхній правий край біля правого краю вікна")

    if provaly:
        print("  ❌ зауваження:")
        for p in provaly:
            print(f"     · {p}")
        uspih = False
    else:
        print("  ✅ форма повна, поля в колонку з підписами, кнопки внизу праворуч")
        uspih = True

    if polia:
        shyrshe = sum(1 for a, b in zip(polia, [d for d in pislia["vidzhety"] if d["klas"] == "Entry"])
                      if b["w"] > a["w"] + 50)
        if shyrshe == len(polia):
            print("  ⭐ вікно розтягнули на 200 px — поля розтягнулись разом із ним")
        else:
            print("  ·  вікно розтягнули на 200 px — поля лишились тієї самої ширини"
                  + (" (для place це очікувано — запишіть у vysnovok.md)" if menedzher == "place" else
                     " (⭐1: weight і sticky)" if menedzher == "grid" else ""))
    return uspih


def main():
    menedzhery = [sys.argv[1]] if len(sys.argv) > 1 else ["grid", "pack", "place"]
    rezultaty = {m: perevirka(m) for m in menedzhery}
    if len(menedzhery) == 3:
        gotovo = [m for m, r in rezultaty.items() if r]
        print(f"\nРазом: {len(gotovo)} з 3 форм ✅   (мінімум для зарахування — grid і ще одна)")


if __name__ == "__main__":
    main()
