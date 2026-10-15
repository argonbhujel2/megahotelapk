import sys
import sqlite3
from pathlib import Path

sys.path.insert(0, str(Path("backend").resolve()))

from app import create_app
from app.config import Config
from app.extensions import db

class SafeTestConfig(Config):
    ADMIN_BOOTSTRAP_ENABLED = False

app = create_app(SafeTestConfig)
local_path = Path("backend/instance/local.db")

with app.app_context():
    model_tables = set(db.metadata.tables.keys())
    connection = sqlite3.connect(
        f"file:{local_path.resolve()}?mode=ro", uri=True
    )
    try:
        local_tables = {
            row[0] for row in connection.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
        }

        print("MODEL TABLE COUNT:", len(model_tables))
        print("LOCAL TABLE COUNT:", len(local_tables))
        print("TABLES MISSING FROM LOCAL DB:")
        for name in sorted(model_tables - local_tables):
            print("  ", name)

        print("LOCAL TABLES NOT IN MODEL METADATA:")
        for name in sorted(local_tables - model_tables):
            print("  ", name)

        for table_name in ("categories", "food_items"):
            print(f"\n--- {table_name} columns ---")
            local_columns = [
                row[1] for row in connection.execute(
                    f'PRAGMA table_info("{table_name}")'
                )
            ]
            model_columns = list(db.metadata.tables[table_name].columns.keys())
            print("LOCAL:", ", ".join(local_columns))
            print("MODEL:", ", ".join(model_columns))
            print("MODEL COLUMNS MISSING LOCALLY:",
                  ", ".join(sorted(set(model_columns) - set(local_columns))) or "none")
    finally:
        connection.close()
