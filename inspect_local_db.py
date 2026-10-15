import sqlite3
from pathlib import Path

candidates = [
    Path("backend/instance/local.db"),
    Path("backend/local.db"),
    Path("instance/local.db"),
]

db_path = next((p for p in candidates if p.exists()), None)

if db_path is None:
    print("LOCAL DATABASE NOT FOUND IN EXPECTED PATHS")
    for p in candidates:
        print(p, "exists:", p.exists())
else:
    print("LOCAL DATABASE FOUND:", db_path)
    connection = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
    try:
        tables = connection.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """).fetchall()

        print("LOCAL TABLE COUNT:", len(tables))
        for (name,) in tables:
            try:
                count = connection.execute(
                    f'SELECT COUNT(*) FROM "{name}"'
                ).fetchone()[0]
                print(f"TABLE: {name} | ROWS: {count}")
            except Exception as exc:
                print(f"TABLE: {name} | COUNT ERROR: {exc}")
    finally:
        connection.close()
