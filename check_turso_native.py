import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv(Path("backend/.env"), override=True)

host = os.getenv("TURSO_DATABASE_URL", "").replace("libsql://", "").strip("/")
token = os.getenv("TURSO_AUTH_TOKEN", "")

if not host or not token:
    print("RESULT: URL or token missing")
    raise SystemExit(1)

try:
    engine = create_engine(
        URL.create(
            "sqlite+libsql_native",
            host=host,
            query={"secure": "true"},
        ),
        connect_args={"auth_token": token},
    )
    with engine.connect() as connection:
        print("QUERY RESULT:", connection.execute(text("SELECT 1")).scalar())
    print("RESULT: SQLALCHEMY NATIVE CONNECTION OK")
except Exception as exc:
    print("RESULT: SQLALCHEMY NATIVE CONNECTION FAILED")
    print("ERROR TYPE:", type(exc).__name__)
    print("ERROR:", str(exc)[:300])
finally:
    if "engine" in locals():
        engine.dispose()
