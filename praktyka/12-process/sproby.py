"""Робота 12, крок 1: перевірка передбачень — правила форми «Заявка на відпустку».

Запускайте ТІЛЬКИ після того, як записали передбачення в peredbachennia.md:
    python praktyka/12-process/sproby.py

Правила нижче — це ДАНІ, а не код: маленький рушій читає їх і виконує,
так само як це робить low-code платформа.
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# When — подія; If — умова (або None); Then / Else — список дій
PRAVYLA = [
    {"nazva": "R1", "when": "форма відкрилась", "if": None,
     "then": [("сховати", "Причина"), ("вимкнути", "Надіслати")], "else": []},
    {"nazva": "R2", "when": "змінилось Днів", "if": lambda f: f["Днів"] > 14,
     "then": [("показати", "Причина"), ("обовʼязкове", "Причина")],
     "else": [("сховати", "Причина"), ("необовʼязкове", "Причина")]},
    {"nazva": "R3", "when": "змінилось Згода", "if": lambda f: f["Згода"],
     "then": [("увімкнути", "Надіслати")], "else": [("вимкнути", "Надіслати")]},
    {"nazva": "R4", "when": "натиснуто Надіслати",
     "if": lambda f: "Причина" in f["обовʼязкові"] and not f["Причина"],
     "then": [("повідомити", "Заповніть обовʼязкові поля")],
     "else": [("повідомити", "Надіслано керівнику")]},
    {"nazva": "R5", "when": "натиснуто Надіслати", "if": lambda f: f["Днів"] > 28,
     "then": [("повідомити", "Потрібне погодження директора")], "else": []},
]

TEKST_PRAVYL = """R1  When форма відкрилась                 Then сховати «Причина»; вимкнути «Надіслати»
R2  When змінилось «Днів»   If Днів > 14    Then показати «Причина», зробити обовʼязковим
                                            Else сховати «Причина», зробити необовʼязковим
R3  When змінилось «Згода»  If Згода = так  Then увімкнути «Надіслати»   Else вимкнути «Надіслати»
R4  When натиснуто «Надіслати»  If «Причина» обовʼязкова й порожня
                                            Then повідомити «Заповніть обовʼязкові поля»
                                            Else повідомити «Надіслано керівнику»
R5  When натиснуто «Надіслати»  If Днів > 28  Then повідомити «Потрібне погодження директора»"""


class Forma:
    def __init__(self):
        self.f = {"Днів": 0, "Згода": False, "Причина": "", "обовʼязкові": set(),
                  "видимі": {"Днів", "Згода", "Причина"}, "увімкнені": {"Надіслати"}}
        self.povidomlennia = []
        self.podiia("форма відкрилась")

    def diia(self, shcho, obiekt):
        f = self.f
        {"сховати": lambda: f["видимі"].discard(obiekt), "показати": lambda: f["видимі"].add(obiekt),
         "вимкнути": lambda: f["увімкнені"].discard(obiekt), "увімкнути": lambda: f["увімкнені"].add(obiekt),
         "обовʼязкове": lambda: f["обовʼязкові"].add(obiekt),
         "необовʼязкове": lambda: f["обовʼязкові"].discard(obiekt),
         "повідомити": lambda: self.povidomlennia.append(obiekt)}[shcho]()

    def podiia(self, nazva):
        for p in PRAVYLA:                       # усі правила з цією подією — по черзі
            if p["when"] != nazva:
                continue
            gilka = p["then"] if p["if"] is None or p["if"](self.f) else p["else"]
            for shcho, obiekt in gilka:
                self.diia(shcho, obiekt)

    def vvesty(self, pole, znachennia):
        self.f[pole] = znachennia
        self.podiia(f"змінилось {pole}")

    def natysnuty(self, knopka):
        if knopka not in self.f["увімкнені"]:
            self.povidomlennia.append(f"(кнопка «{knopka}» вимкнена — нічого не сталося)")
            return
        self.podiia(f"натиснуто {knopka}")

    def stan(self):
        return (f"«Причина» {'видно' if 'Причина' in self.f['видимі'] else 'сховано'}; "
                f"«Надіслати» {'увімкнена' if 'Надіслати' in self.f['увімкнені'] else 'вимкнена'}; "
                f"повідомлення: {self.povidomlennia or '—'}")


def a():
    f = Forma(); f.vvesty("Днів", 20); return f


def b():
    f = Forma(); f.vvesty("Днів", 20); f.vvesty("Днів", 5); return f


def c():
    f = Forma(); f.vvesty("Днів", 5); f.natysnuty("Надіслати"); return f


def d():
    f = Forma(); f.vvesty("Днів", 20); f.vvesty("Згода", True); f.natysnuty("Надіслати"); return f


def e():
    f = Forma(); f.vvesty("Днів", 30); f.vvesty("Згода", True); f.vvesty("Причина", "лікування")
    f.natysnuty("Надіслати"); return f


SPROBY = [
    ("A", "відкрили форму, Днів = 20", a),
    ("B", "Днів = 20, потім виправили на Днів = 5", b),
    ("C", "Днів = 5, «Згода» не поставлена, натиснули «Надіслати»", c),
    ("D", "Днів = 20, «Згода» = так, «Причина» порожня, «Надіслати»", d),
    ("E", "Днів = 30, «Згода» = так, «Причина» = «лікування», «Надіслати»", e),
]

print("Правила форми:\n")
print(TEKST_PRAVYL)
print()
for bukva, opys, f in SPROBY:
    print(f"{bukva}  {opys}\n   → {f().stan()}\n")
