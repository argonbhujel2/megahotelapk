import os
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv(Path("backend/.env"), override=True)

url = os.getenv("TURSO_DATABASE_URL", "")
token = os.getenv("TURSO_AUTH_TOKEN", "")
db_url = os.getenv("DATABASE_URL", "")

print("TURSO URL PRESENT:", bool(url))
print("TURSO URL SCHEME:", urlparse(url).scheme if url else "MISSING")
print("TURSO URL HOST:", urlparse(url).hostname if url else "MISSING")
print("TURSO TOKEN PRESENT:", bool(token))
print("SQLALCHEMY URL SCHEME:", db_url.split(":", 1)[0] if db_url else "MISSING")
