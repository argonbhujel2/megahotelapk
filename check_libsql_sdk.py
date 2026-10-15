import os
from pathlib import Path
from dotenv import load_dotenv
import libsql

load_dotenv(Path("backend/.env"), override=True)

url = os.getenv("TURSO_DATABASE_URL", "")
token = os.getenv("TURSO_AUTH_TOKEN", "")

try:
    conn = libsql.connect(database=url, auth_token=token)
    result = conn.execute("SELECT 1").fetchone()
    print("RESULT: LIBSQL SDK CONNECTION OK" if result else "RESULT: QUERY RETURNED NO ROW")
    conn.close()
except Exception as exc:
    print("RESULT: LIBSQL SDK CONNECTION FAILED")
    print("ERROR TYPE:", type(exc).__name__)
    print("ERROR:", str(exc)[:300])
