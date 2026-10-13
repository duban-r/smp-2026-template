"""Перевіряє hra.py: запускає гру без вікна на ~4 секунди й дивиться, що відбувається.

Запуск (з кореня репозиторію):
    python praktyka/13-hra/perevir.py

Перші пів секунди клавіші не натиснуті (чи рухається щось саме?), потім «натискається»
стрілка вправо. Наприкінці надсилається QUIT — як хрестик вікна. Ваш файл не змінюється.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

FAIL = Path(__file__).resolve().parent / "hra.py"

ZAPUSK = r'''
import hashlib, json, os, runpy, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame

st = {"kadr": 0, "tick": [], "teksty": [], "hashi": {}, "quit_kadr": None, "zakinchylas": None}
QUIT_NA = 240

_Clock = pygame.time.Clock
class Clock:
    def __init__(self, *a, **k): self._c = _Clock(*a, **k)
    def tick(self, fps=0, *a):
        st["tick"].append(fps)
        return self._c.tick(fps, *a)
    def __getattr__(self, n): return getattr(self._c, n)
pygame.time.Clock = Clock

def obhortka(klas):
    class Shryft:
        def __init__(self, *a, **k): self._f = klas(*a, **k)
        def render(self, tekst, *a, **k):
            if len(st["teksty"]) < 400:
                st["teksty"].append(str(tekst))
            return self._f.render(tekst, *a, **k)
        def __getattr__(self, n): return getattr(self._f, n)
    return Shryft
pygame.font.Font = obhortka(pygame.font.Font)
_SysFont = pygame.font.SysFont
pygame.font.SysFont = lambda *a, **k: obhortka(lambda: _SysFont(*a, **k))()

class Klavishi:
    def __getitem__(self, kod):
        return 40 <= st["kadr"] <= 140 and kod in (pygame.K_RIGHT, pygame.K_d)
pygame.key.get_pressed = lambda: Klavishi()

def pislia_kadru():
    st["kadr"] += 1
    k = st["kadr"]
    s = pygame.display.get_surface()
    if s is not None and k in (5, 35, 60, 120):
        st["hashi"][k] = hashlib.md5(pygame.image.tobytes(s, "RGB")).hexdigest()[:10]
    if k == 40:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT, mod=0, unicode="", scancode=79))
    if k == 140:
        pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_RIGHT, mod=0, unicode="", scancode=79))
    if k == QUIT_NA:
        pygame.event.post(pygame.event.Event(pygame.QUIT))
    if k > QUIT_NA + 60:
        st["zakinchylas"] = "QUIT ігнорується"
        raise SystemExit

for imia in ("flip", "update"):
    stara = getattr(pygame.display, imia)
    def nova(*a, _s=stara, **k):
        r = _s(*a, **k)
        pislia_kadru()
        return r
    setattr(pygame.display, imia, nova)

try:
    runpy.run_path(sys.argv[1], run_name="__main__")
    if st["zakinchylas"] is None:
        st["zakinchylas"] = "QUIT" if st["kadr"] >= QUIT_NA else f"гра закінчилась сама на кадрі {st['kadr']}"
except SystemExit:
    if st["zakinchylas"] is None:
        st["zakinchylas"] = "QUIT" if st["kadr"] >= QUIT_NA else f"sys.exit на кадрі {st['kadr']}"
print("@@ZVIT@@" + json.dumps(st, ensure_ascii=False))
'''


def main():
    if not FAIL.exists():
        sys.exit(f"Не знайдено {FAIL}. Візьміть заготовку з шаблону (крок 0 інструкції).")
    try:
        import pygame  # noqa: F401
    except ImportError:
        sys.exit("pygame не встановлено:  python -m pip install pygame-ce")
    kod = re.sub(r"#.*", "", FAIL.read_text(encoding="utf-8"))     # коментарі не рахуються
    try:
        r = subprocess.run([sys.executable, "-c", ZAPUSK, str(FAIL)], capture_output=True, text=True,
                           encoding="utf-8", timeout=60, env={**os.environ, "PYTHONUTF8": "1"})
    except subprocess.TimeoutExpired:
        sys.exit("❌ Гра не завершилась за 60 секунд — у циклі немає display.flip()? (перевірка рахує кадри по ньому)")
    zvit = next((json.loads(x[8:]) for x in r.stdout.splitlines() if x.startswith("@@ZVIT@@")), None)
    if zvit is None:
        ostannii = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "невідома помилка"
        print(f"❌ Гра впала: {ostannii}")
        return

    zaraz = 0
    print(f"Кадрів: {zvit['kadr']}; завершення: {zvit['zakinchylas']}\n")
    if zvit["zakinchylas"] == "QUIT ігнорується":
        print("⚠️  гра не реагує на QUIT — хрестиком вікно не закрити: if podiia.type == pygame.QUIT")

    # 1. клавіші — за текстом коду
    if re.search(r"get_pressed|KEYDOWN", kod) and re.search(r"K_\w+", kod):
        print("✅ 1. гравець керується клавішами (get_pressed / KEYDOWN і K_…)")
        zaraz += 1
    else:
        print("❌ 1. у коді немає опитування клавіш: klavishi = pygame.key.get_pressed(); if klavishi[pygame.K_LEFT]: …")

    # 2. рух сам
    h = zvit["hashi"]
    if "5" in h and "35" in h and h["5"] != h["35"]:
        print("✅ 2. щось рухається саме — кадр 35 відрізняється від кадру 5 без жодної клавіші")
        zaraz += 1
    else:
        print("❌ 2. без клавіш екран не змінюється — потрібен обʼєкт, що рухається сам (x += швидкість щокадру)")

    # 3. зіткнення — за текстом коду
    if re.search(r"collide\w*|colliderect|spritecollide", kod):
        print("✅ 3. зіткнення перевіряються (colliderect / spritecollide …)")
        zaraz += 1
    else:
        print("❌ 3. не знайдено перевірки зіткнення: if gravets.colliderect(vorog): …")

    # 4. текст із числом
    z_chyslom = [t for t in zvit["teksty"] if re.search(r"\d", t)]
    if z_chyslom:
        rizni = list(dict.fromkeys(z_chyslom))
        print(f"✅ 4. на екрані текст із числом: «{rizni[0]}»" + (f" … «{rizni[-1]}»" if len(rizni) > 1 else ""))
        zaraz += 1
        if len(rizni) > 1:
            print("   ⭐ за 4 секунди число змінилось — наслідок зіткнення працює")
    elif zvit["teksty"]:
        print(f"❌ 4. текст є («{zvit['teksty'][0]}»), але без числа — покажіть рахунок: f\"Рахунок: {{rakhunok}}\"")
    else:
        print("❌ 4. текст не виводиться: ekran.blit(shryft.render(f\"Рахунок: {rakhunok}\", True, (255, 255, 255)), (10, 10))")

    # 5. 60 FPS
    tick = zvit["tick"]
    if tick and all(t == 60 for t in tick):
        print("✅ 5. hodynnyk.tick(60) на кожному кадрі")
        zaraz += 1
    elif not tick:
        print("❌ 5. Clock.tick не викликається — гра крутиться з максимальною швидкістю")
    else:
        print(f"❌ 5. tick викликається з {sorted(set(tick))} — потрібно 60")

    print(f"\nРазом: {zaraz} з 5 ✅   (мінімум для зарахування — 4 з 5)")


if __name__ == "__main__":
    main()
