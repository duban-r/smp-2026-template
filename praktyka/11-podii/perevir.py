"""Перевіряє ваш застосунок з подіями: kalkulyator.py або notatnyk.py.

Запуск (з кореня репозиторію):
    python praktyka/11-podii/perevir.py
    python praktyka/11-podii/perevir.py praktyka/11-podii/mii_fail.py   — інший файл

Запускає застосунок, сам «натискає» клавіші й кнопки (Enter, Esc, неправильне
введення) і дивиться, що змінилось. Діалоги (messagebox, вибір файлу) підмінено —
вони не відкриваються. Наприкінці вікно закривається. Ваш файл не змінюється.
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

ZAMIST_MAINLOOP = r'''
import json, re, runpy, sys, tkinter as tk
from tkinter import filedialog, messagebox

pomylky, dialohy = [], []
lich = {"StringVar": 0, "trace": 0}
_sv = tk.StringVar.__init__
def _sv_init(self, *a, **k):
    lich["StringVar"] += 1
    _sv(self, *a, **k)
tk.StringVar.__init__ = _sv_init
_tr = tk.Variable.trace_add
def _trace(self, *a, **k):
    lich["trace"] += 1
    return _tr(self, *a, **k)
tk.Variable.trace_add = _trace
tk.Tk.report_callback_exception = lambda self, e, v, tb: pomylky.append(f"{e.__name__}: {v}")
for imia in ("showinfo", "showwarning", "showerror"):
    setattr(messagebox, imia, lambda *a, _i=imia, **k: dialohy.append(_i + ": " + " ".join(map(str, a))) or "ok")
for imia in ("askyesno", "askokcancel", "askquestion", "askretrycancel", "askyesnocancel"):
    setattr(messagebox, imia, lambda *a, **k: True)
for imia in ("asksaveasfilename", "askopenfilename", "askdirectory"):
    setattr(filedialog, imia, lambda *a, **k: "")

ZAKRYTY = re.compile(r"закр|вих|exit|quit|close", re.I)

def vsi(w):
    for c in w.winfo_children():
        yield c
        yield from vsi(c)

def tekst(w):
    klas = w.winfo_class()
    try:
        if klas == "Text":
            return w.get("1.0", "end-1c")
        if klas in ("Entry", "Spinbox", "TEntry"):
            return w.get()
        zm = str(w.cget("textvariable")) if "textvariable" in w.keys() else ""
        return w.getvar(zm) if zm else str(w.cget("text"))
    except tk.TclError:
        return ""

def zrizok(korin):
    return [tekst(w) for w in vsi(korin) if w.winfo_class() in ("Label", "TLabel", "Message", "Entry", "Text", "Spinbox")] + list(dialohy)

def zapovnyty(polia, znachennia):
    for i, p in enumerate(polia):
        z = znachennia[i % len(znachennia)]
        if p.winfo_class() == "Text":
            p.delete("1.0", "end"); p.insert("1.0", z)
        else:
            p.delete(0, "end"); p.insert(0, z)

def natysnuty(korin, w, poslidovnist):
    w.focus_force(); korin.update()
    w.event_generate(poslidovnist); korin.update()

def zamist(self=None, n=0):
    korin = tk._default_root
    korin.update()
    vidzhety = list(vsi(korin))
    zvit = {}
    podii = set()
    for w in [korin] + vidzhety:
        for s in w.bind():
            podii.add(s)
        if "command" in w.keys() and str(w.cget("command")):
            podii.add("command " + w.winfo_class())
    podii |= {"bind_all " + s for s in korin.bind_class("all")} - POCHATKOVI_ALL
    zvit["podii"] = sorted(podii)
    zvit["bind"] = sorted(s for s in podii if s.startswith("<") or s.startswith("bind_all"))
    polia = [w for w in vidzhety if w.winfo_class() in ("Entry", "Text", "Spinbox", "TEntry")]
    knopky = [w for w in vidzhety if w.winfo_class() in ("Button", "TButton")
              and not ZAKRYTY.search(str(w.cget("text"))) and str(w.cget("command"))]
    zvit["polia"] = len(polia)
    zvit["knopky"] = [str(k.cget("text")) for k in knopky]
    zvit["StringVar"] = sum(1 for w in vidzhety if w.winfo_class() in ("Label", "Entry", "TLabel", "TEntry", "Spinbox")
                            and str(w.cget("textvariable")))
    zvit["trace"] = lich["trace"]
    pershe = next((p for p in polia if p.winfo_class() != "Text"), polia[0] if polia else korin)

    # 2. Enter = головна кнопка
    zapovnyty(polia, ["12", "3"]); korin.update(); do = zrizok(korin)
    natysnuty(korin, pershe, "<Return>"); pislia_enter = zrizok(korin)
    zvit["enter_zminyv"] = pislia_enter != do
    zbig = []
    for k in knopky:
        zapovnyty(polia, ["12", "3"]); dialohy.clear(); korin.update()
        k.invoke(); korin.update()
        if not korin.winfo_exists():
            break
        if zrizok(korin) == pislia_enter:
            zbig.append(str(k.cget("text")))
    zvit["enter_yak_knopka"] = zbig

    # 3. Escape очищає
    zapovnyty(polia, ["abc", "xyz"]); korin.update()
    natysnuty(korin, pershe, "<Escape>")
    zvit["escape_ochystyv"] = bool(polia) and all(tekst(p) in ("", "0") for p in polia)

    # 4. неправильне введення не валить
    pomylky.clear()
    for nabir in (["abc", "xyz"], ["", ""], ["5", "0"], ["1e999", "-"]):
        zapovnyty(polia, nabir); korin.update()
        natysnuty(korin, pershe, "<Return>")
        for k in knopky:
            k.invoke(); korin.update()
    zvit["pomylky"] = sorted(set(pomylky))
    print("@@ZVIT@@" + json.dumps(zvit, ensure_ascii=False))
    korin.destroy()

_t = tk.Tcl()
POCHATKOVI_ALL = {"bind_all " + s for s in tk.Tk().bind_class("all")}
tk._default_root.destroy()
tk._default_root = None
tk.Misc.mainloop = zamist
tk.mainloop = zamist
runpy.run_path(sys.argv[1], run_name="__main__")
'''


def znaity_fail():
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    for imia in ("kalkulyator.py", "notatnyk.py"):
        if (TUT / imia).exists():
            return TUT / imia
    return None


def main():
    fail = znaity_fail()
    if not fail or not fail.exists():
        sys.exit("Не знайдено kalkulyator.py чи notatnyk.py у praktyka/11-podii/. "
                 "Назвіть файл так або передайте шлях: python praktyka/11-podii/perevir.py мій_файл.py")
    print(f"Перевіряю {fail.name}\n")
    try:
        r = subprocess.run([sys.executable, "-c", ZAMIST_MAINLOOP, str(fail)], capture_output=True,
                           text=True, encoding="utf-8", timeout=60, env={**os.environ, "PYTHONUTF8": "1"})
    except subprocess.TimeoutExpired:
        sys.exit("❌ Застосунок не відповів за 60 секунд — у ньому input(), time.sleep() чи нескінченний цикл?")
    zvit = next((json.loads(x[8:]) for x in r.stdout.splitlines() if x.startswith("@@ZVIT@@")), None)
    if zvit is None:
        ostannii = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "у файлі немає mainloop()"
        print(f"❌ Застосунок не запустився: {ostannii}")
        if "takes 0 positional arguments" in r.stderr:
            print("   ← обробник для bind отримує подію: def f(podiia=None)")
        return

    zaraz = 0
    podii = zvit["podii"]
    print(f"Знайдені події ({len(podii)}): {', '.join(podii) or '—'}")

    if len(podii) >= 3 and zvit["bind"]:
        print("✅ 1. три й більше різних подій, серед них через bind")
        zaraz += 1
    elif not zvit["bind"]:
        print("❌ 1. немає жодної події через bind — лише command кнопок")
    else:
        print(f"❌ 1. різних подій {len(podii)}, а треба щонайменше 3")

    if zvit["enter_yak_knopka"] and zvit["enter_zminyv"]:
        print(f"✅ 2. Enter у полі робить те саме, що кнопка «{zvit['enter_yak_knopka'][0]}»")
        zaraz += 1
    elif zvit["enter_zminyv"]:
        print("❌ 2. Enter щось робить, але не те саме, що кнопка — звʼяжіть <Return> з ТІЄЮ САМОЮ функцією")
    elif any("takes 0 positional" in x for x in zvit["pomylky"]):
        print("❌ 2. Enter викликає функцію, але вона падає: обробник для bind отримує подію — def f(podiia=None)")
    else:
        print("❌ 2. після Enter у вікні нічого не змінилось (результат має бути видно у вікні, не в консолі) — pole.bind(\"<Return>\", …)")

    if zvit["escape_ochystyv"]:
        print("✅ 3. Esc очищає поля")
        zaraz += 1
    else:
        print("❌ 3. після Esc у полях лишився текст — vikno.bind(\"<Escape>\", ochystyty)")

    if not zvit["pomylky"]:
        print("✅ 4. «abc», порожні поля, ділення на нуль — без жодної помилки Python")
        zaraz += 1
    else:
        print("❌ 4. на неправильному введенні Python падає:")
        for p in zvit["pomylky"][:4]:
            print(f"     {p}")
        if any("takes 0 positional" in p for p in zvit["pomylky"]):
            print("     ← обробник для bind отримує подію: def f(podiia=None)")
        else:
            print("     ← try / except ValueError навколо float(…), окремо — ділення на нуль")

    if zvit["StringVar"]:
        print("✅ 5. напис або поле повʼязані зі StringVar (textvariable)")
        zaraz += 1
    else:
        print("❌ 5. немає напису чи поля, повʼязаного з StringVar — tk.Label(…, textvariable=rez) або tk.Entry(…, textvariable=…)")

    if zvit["trace"]:
        print("⭐ trace_add є — щось оновлюється під час набору")
    print(f"\nРазом: {zaraz} з 5 вимог ✅   (мінімум для зарахування — 4 з 5)")


if __name__ == "__main__":
    main()
