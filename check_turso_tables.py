import sys
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path("backend").resolve()))

from app import create_app
from app.config import Config
from app.extensions import db

class SafeTestConfig(Config):
    ADMIN_BOOTSTRAP_ENABLED = False

app = create_app(SafeTestConfig)

with app.app_context():
    try:
        with db.engine.connect() as connection:
            rows = connection.execute(text("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)).fetchall()

        print("TURSO TABLE COUNT:", len(rows))
        for row in rows:
            print("TABLE:", row[0])

        response = app.test_client().get("/api/v1/menu/categories?lang=en")
        print("MENU CATEGORIES STATUS:", response.status_code)
        print("MENU RESPONSE PREVIEW:", response.get_data(as_text=True)[:500])

    except Exception as exc:
        print("RESULT: DATABASE CONTENT CHECK FAILED")
        print("ERROR TYPE:", type(exc).__name__)
        print("ERROR:", str(exc)[:350])
