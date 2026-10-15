import sys
import sqlite3
from pathlib import Path
from datetime import datetime, date

sys.path.insert(0, str(Path("backend").resolve()))

from app import create_app
from app.config import Config
from app.extensions import db
from sqlalchemy import text, DateTime, Date

class SafeTestConfig(Config):
    ADMIN_BOOTSTRAP_ENABLED = False

app = create_app(SafeTestConfig)
source_path = Path("backend/instance/local.db").resolve()
table_names = ("categories", "food_items")

def convert_value(value, column):
    if value is None:
        return None
    if isinstance(column.type, DateTime) and isinstance(value, str):
        return datetime.fromisoformat(value)
    if isinstance(column.type, Date) and not isinstance(column.type, DateTime) and isinstance(value, str):
        return date.fromisoformat(value)
    return value

with app.app_context():
    source = sqlite3.connect(
        f"file:{source_path}?mode=ro", uri=True
    )
    source.row_factory = sqlite3.Row

    try:
        data = {
            name: [dict(row) for row in source.execute(
                f'SELECT * FROM "{name}"'
            ).fetchall()]
            for name in table_names
        }
    finally:
        source.close()

    print("LOCAL CATEGORIES:", len(data["categories"]))
    print("LOCAL FOOD ITEMS:", len(data["food_items"]))

    if len(data["categories"]) != 6 or len(data["food_items"]) != 13:
        raise SystemExit("STOPPED: Local menu counts differ from expected counts.")

    try:
        with db.engine.begin() as connection:
            for name in table_names:
                count = connection.execute(
                    text(f'SELECT COUNT(*) FROM "{name}"')
                ).scalar_one()
                if count != 0:
                    raise RuntimeError(
                        f"STOPPED: Turso table {name} already has {count} rows. "
                        "No rows were migrated."
                    )

            for name in table_names:
                table = db.metadata.tables[name]
                records = [
                    {
                        key: convert_value(value, table.c[key])
                        for key, value in row.items()
                        if key in table.c
                    }
                    for row in data[name]
                ]
                if records:
                    connection.execute(table.insert(), records)
                print(f"INSERTED {name.upper()}:", len(records))

        print("MIGRATION RESULT: SUCCESS")

    except Exception as exc:
        print("MIGRATION RESULT: FAILED")
        print("ERROR TYPE:", type(exc).__name__)
        print("ERROR:", str(exc)[:400])
