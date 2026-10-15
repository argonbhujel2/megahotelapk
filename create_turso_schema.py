import sys
from pathlib import Path

sys.path.insert(0, str(Path("backend").resolve()))

from app import create_app
from app.config import Config
from app.extensions import db
from sqlalchemy import text

class SafeTestConfig(Config):
    ADMIN_BOOTSTRAP_ENABLED = False

app = create_app(SafeTestConfig)

with app.app_context():
    try:
        db.create_all()
        print("SCHEMA CREATION: COMPLETED")

        with db.engine.connect() as connection:
            tables = connection.execute(text("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)).fetchall()

        print("TURSO TABLE COUNT:", len(tables))
        for row in tables:
            print("TABLE:", row[0])

    except Exception as exc:
        print("SCHEMA CREATION: FAILED")
        print("ERROR TYPE:", type(exc).__name__)
        print("ERROR:", str(exc)[:500])
