from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path("backend/.env"), override=True)

url = os.getenv("DATABASE_URL")
token = os.getenv("TURSO_AUTH_TOKEN")

if not url or not token:
    print("RESULT: Missing database URL or token")
    raise SystemExit(1)

from sqlalchemy import create_engine, text

engine = create_engine(url, connect_args={"auth_token": token})

try:
    with engine.connect() as conn:
        print("SELECT 1:", conn.execute(text("SELECT 1")).scalar())
    print("RESULT: TURSO CONNECTION OK")
except Exception as exc:
    print("RESULT: CONNECTION FAILED")
    print("ERROR TYPE:", type(exc).__name__)
    print("ERROR:", str(exc)[:400])
finally:
    engine.dispose()
