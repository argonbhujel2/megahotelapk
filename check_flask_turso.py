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

try:
    with app.app_context():
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()
            print("DATABASE QUERY RESULT:", result)
            print("DATABASE DRIVER:", db.engine.dialect.name, db.engine.dialect.driver)

    response = app.test_client().get("/health")
    print("HEALTH STATUS:", response.status_code)
    print("RESULT: FLASK TURSO CONNECTION OK")
except Exception as exc:
    print("RESULT: FLASK TURSO CONNECTION FAILED")
    print("ERROR TYPE:", type(exc).__name__)
    print("ERROR:", str(exc)[:400])
