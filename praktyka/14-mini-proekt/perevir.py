"""Перевіряє роботу 14: файли міні-проєкту і proekt.md.

Запуск (з кореня репозиторію):
    python praktyka/14-mini-proekt/perevir.py

Чи правильно працює ваш проєкт, скрипт не знає — це видно на розборі.
Він перевіряє, що все на місці: файл проєкту, заповнені розділи, результат,
пояснення особливості мови.
"""
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

TUT = Path(__file__).resolve().parent
SLUZHBOVI = {"readme.md", "proekt.md", "perevir.py"}
KARTYNKY = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
TEMY = {str(n) for n in range(1, 27)} | {f"к{n}" for n in range(1, 7)} | {f"k{n}" for n in range(1, 7)}

# розширення → мова, щоб підказати, якщо файл не той
ROZSHYRENNIA = {
    ".yml": "YAML / GitHub Actions / OpenAPI", ".yaml": "YAML / GitHub Actions / OpenAPI",
    ".mmd": "Mermaid", ".md": "Markdown (Mermaid усередині)", ".dot": "Graphviz", ".gv": "Graphviz",
    ".puml": "PlantUML", ".json": "JSON / Vega-Lite / JSON Schema", ".tex": "LaTeX", ".typ": "Typst",
    ".html": "HTML", ".css": "CSS", ".svg": "SVG", ".j2": "Jinja2", ".jinja": "Jinja2",
    ".sql": "SQL", ".graphql": "GraphQL", ".gql": "GraphQL", ".txt": "текст", ".awk": "awk",
    ".toml": "TOML", ".tf": "Terraform", ".sol": "Solidity", ".gcode": "G-code", ".nc": "G-code",
    ".ahk": "AutoHotkey", ".lark": "Lark", ".xpath": "XPath", ".py": "Python",
}

ROZDILY = ["тема", "що робить проєкт", "як запустити або подивитись", "результат",
           "особливість мови", "межа", "ai"]


def nazva_rozdilu(nazva):
    return "AI" if nazva == "ai" else nazva.capitalize()


def rozdily(tekst):
    chastyny = re.split(r"^##\s+(.+)$", tekst, flags=re.M)
    return {n.strip().lower(): v.strip() for n, v in zip(chastyny[1::2], chastyny[2::2])}


def bez_komentariv(tekst):
    return re.sub(r"<!--.*?-->", "", tekst, flags=re.S).strip()


def slova(tekst):
    tekst = re.sub(r"```.*?```", " ", tekst, flags=re.S)
    return re.findall(r"[\wʼ'’-]+", tekst)


def fajly_proektu():
    print("== файли проєкту")
    znaideni = []
    for f in sorted(TUT.rglob("*")):
        if not f.is_file() or f.name.lower() in SLUZHBOVI or "__pycache__" in f.parts:
            continue
        if f.suffix.lower() in KARTYNKY:
            continue
        try:
            ryadky = [r for r in f.read_text(encoding="utf-8").splitlines() if r.strip()]
        except (UnicodeDecodeError, OSError):
            continue
        mova = ROZSHYRENNIA.get(f.suffix.lower(), "невідоме розширення")
        znaideni.append((f, len(ryadky)))
        poznaka = "✅" if len(ryadky) >= 10 else "⚠️"
        dodatok = "" if len(ryadky) >= 10 else "  ← замало для проєкту, хоча б 10 непорожніх рядків"
        print(f"  {poznaka} {f.relative_to(TUT)} ({mova}) — непорожніх рядків: {len(ryadky)}{dodatok}")
    if not znaideni:
        print("  ❌ немає файлу проєкту — покладіть у цю теку файл вашою мовою "
              "(браузерний проєкт — скопіюйте текст у файл)")
        return False
    return max(n for _, n in znaideni) >= 10


def proekt():
    fail = TUT / "proekt.md"
    print("\n== proekt.md")
    if not fail.exists():
        print("  ❌ немає файлу — візьміть із шаблону (крок 0)")
        return False
    tekst = bez_komentariv(fail.read_text(encoding="utf-8"))
    vse_dobre = True

    zagolovok = tekst.splitlines()[0] if tekst else ""
    if "…" in zagolovok or not zagolovok.startswith("#"):
        print("  ❌ у заголовку немає назви мови: `# Міні-проєкт: SQL`")
        vse_dobre = False
    else:
        print(f"  ✅ {zagolovok.lstrip('# ').strip()}")

    r = rozdily(tekst)
    for nazva in ROZDILY:
        zmist = r.get(nazva)
        if zmist is None:
            print(f"  ❌ немає розділу «## {nazva_rozdilu(nazva)}» — поверніть його з шаблону")
            vse_dobre = False
        elif not zmist or "…" in zmist:
            print(f"  ❌ розділ «{nazva_rozdilu(nazva)}» порожній або лишились `…`")
            vse_dobre = False

    tema = r.get("тема", "")
    nomer = re.search(r"\b([КкKk]?\d{1,2})\b", tema)
    if tema and "…" not in tema:
        if nomer and nomer.group(1).lower() in TEMY:
            print(f"  ✅ тема {nomer.group(1)}")
        elif "свою" in tema.lower() or "своя" in tema.lower() or "власн" in tema.lower():
            print("  ✅ своя тема — переконайтесь, що її погоджено в чаті")
        else:
            print("  ⚠️ не бачу номера теми: 1–26, К1–К6 або «своя (погоджено)»")

    rezultat = r.get("результат", "")
    if "…" in rezultat:
        rezultat = ""
    kartynka = re.search(r"!\[[^\]]*\]\(([^)]+)\)", rezultat)
    if kartynka:
        shliakh = kartynka.group(1).strip()
        if shliakh.startswith("http") or (TUT / shliakh).exists():
            print("  ✅ результат — зображення")
        else:
            print(f"  ❌ результат посилається на {shliakh}, але такого файлу в теці немає")
            vse_dobre = False
    elif "```" in rezultat:
        print("  ✅ результат — вивід у блоці коду")
    elif rezultat and "…" not in rezultat:
        print("  ⚠️ немає результату: скриншот поруч (`![результат](rezultat.png)`) або вивід у блоці коду")

    osoblyvist = r.get("особливість мови", "")
    if osoblyvist and "…" not in osoblyvist:
        kilkist = len(slova(osoblyvist))
        if kilkist >= 25:
            print(f"  ✅ особливість мови пояснено ({kilkist} слів)")
        else:
            print(f"  ❌ особливість мови — замало ({kilkist} слів): що вона робить простим, "
                  "у якому рядку, як це виглядало б у Python")
            vse_dobre = False
    return vse_dobre


def main():
    print("Робота 14 · міні-проєкт однією предметною мовою\n")
    ok_fajly = fajly_proektu()
    ok_proekt = proekt()
    print()
    if ok_fajly and ok_proekt:
        print("✅ Усе на місці. git add, commit, push — і посилання в чат.")
        print("   На розборі покажете рядок з особливістю мови й скажете, що він робить.")
    else:
        print("Ще не все. Виправте пункти з ❌ і запустіть ще раз.")


if __name__ == "__main__":
    main()
