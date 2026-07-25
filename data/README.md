# Спільні дані

Ці файли **не змінювати** — вони однакові в усіх.

## `access.log`

Журнал вебсервера, **303 рядки**, формат nginx combined.
Потрібен для роботи `praktyka/06-regex-log`.

Один рядок виглядає так:

```
192.168.10.15 - - [17/Mar/2026:08:02:18 +0200] "GET /index.html HTTP/1.1" 200 4478 "-" "curl/8.4.0"
```

Що в ньому є: IP, час, метод, шлях, код відповіді, розмір, реферер, браузер.

⚠️ **Три рядки у файлі зіпсовані навмисно.** Ваш скрипт має їх пропускати,
а не падати. Це частина завдання.

## `chinook.db`

Навчальна база SQLite — магазин музики. Потрібна для робіт
`praktyka/07-sql` і `praktyka/08-sql-join`.

| Таблиця | Рядків | Про що |
|---|---|---|
| `Artist` | 275 | виконавці |
| `Album` | 347 | альбоми |
| `Track` | 3503 | треки |
| `Genre` | 25 | жанри |
| `Customer` | 59 | клієнти магазину |
| `Invoice` | 412 | рахунки |
| `InvoiceLine` | 2240 | позиції рахунків |

Звʼязки: `Artist` → `Album` → `Track`, а також `Genre` → `Track`.

### Як відкрити

**Найпростіше:** [sqliteonline.com](https://sqliteonline.com) →
кнопка **Open DB** → вибрати цей файл.

**Локально:** [DB Browser for SQLite](https://sqlitebrowser.org) —
подвійний клік по файлу.

**З Python:**

```python
import sqlite3
conn = sqlite3.connect("data/chinook.db")
for рядок in conn.execute("SELECT Name FROM Track LIMIT 5"):
    print(рядок)
```

⚠️ Назви таблиць в **однині й з великої літери**: `Track`, а не `tracks`.
