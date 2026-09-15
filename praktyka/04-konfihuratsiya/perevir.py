"""Показує, що бачить Python у файлі конфігурації: кожне значення і його тип.

Запуск (з кореня репозиторію):
    python praktyka/04-konfihuratsiya/perevir.py praktyka/04-konfihuratsiya/pastky.yaml
    python praktyka/04-konfihuratsiya/perevir.py praktyka/04-konfihuratsiya/config.json

Можна кілька файлів одразу. Підтримує .json, .yaml / .yml, .toml.
YAML читається через yaml.safe_load — так, як читає більшість програм на Python.
"""
import json
import sys
import tomllib
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

TYPY = {
    "str": "рядок",
    "int": "ціле число",
    "float": "дробове число",
    "bool": "логічне",
    "NoneType": "порожнє",
    "list": "список",
    "dict": "блок",
    "date": "дата",
    "datetime": "дата й час",
    "time": "час",
}


def prochytaty(shliakh):
    rozshyrennia = shliakh.suffix.lower()
    if rozshyrennia == ".json":
        with open(shliakh, encoding="utf-8") as f:
            return json.load(f)
    if rozshyrennia in (".yaml", ".yml"):
        try:
            import yaml
        except ImportError:
            sys.exit("Немає бібліотеки PyYAML. Встановіть:  python -m pip install pyyaml")
        with open(shliakh, encoding="utf-8") as f:
            return yaml.safe_load(f)
    if rozshyrennia == ".toml":
        with open(shliakh, "rb") as f:
            return tomllib.load(f)
    raise ValueError(f"не знаю формат «{rozshyrennia}»: підтримую .json, .yaml, .yml, .toml")


def ryadok(shliakh, znachennia):
    nazva = type(znachennia).__name__
    print(f"  {shliakh:32} {znachennia!r:30} {TYPY.get(nazva, nazva)}")


def pokazaty(dani, prefiks=""):
    elementy = dani.items() if isinstance(dani, dict) else enumerate(dani)
    for kliuch, znachennia in elementy:
        if isinstance(dani, dict):
            shliakh = f"{prefiks}.{kliuch}" if prefiks else str(kliuch)
        else:
            shliakh = f"{prefiks}[{kliuch}]"
        if isinstance(znachennia, (dict, list)) and znachennia:
            print(f"  {shliakh:32} {'':30} {TYPY[type(znachennia).__name__]}")
            pokazaty(znachennia, shliakh)
        else:
            ryadok(shliakh, znachennia)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    kod = 0
    for imia in sys.argv[1:]:
        shliakh = Path(imia)
        print(f"\n== {shliakh}")
        if not shliakh.exists():
            print("  ❌ файл не знайдено — перевірте шлях")
            kod = 1
            continue
        try:
            dani = prochytaty(shliakh)
        except json.JSONDecodeError as e:
            print(f"  ❌ помилка JSON: рядок {e.lineno}, стовпець {e.colno}: {e.msg}")
            kod = 1
            continue
        except tomllib.TOMLDecodeError as e:
            print(f"  ❌ помилка TOML: {e}")
            kod = 1
            continue
        except ValueError as e:
            print(f"  ❌ {e}")
            kod = 1
            continue
        except Exception as e:  # помилки YAML
            print(f"  ❌ помилка {type(e).__name__}:")
            print("    " + str(e).replace("\n", "\n    "))
            kod = 1
            continue
        if isinstance(dani, (dict, list)):
            pokazaty(dani)
        else:
            ryadok("(увесь файл)", dani)
        print("  ✅ файл розібрано")
    sys.exit(kod)


if __name__ == "__main__":
    main()
