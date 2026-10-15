from pathlib import Path
from dotenv import dotenv_values

values = dotenv_values(Path("backend/.env"))
url = values.get("DATABASE_URL", "") or ""

if url.startswith("sqlite+libsql://"):
    print("DATABASE TYPE: Turso/libSQL SQLAlchemy URL")
elif url.startswith("sqlite:///"):
    print("DATABASE TYPE: Local SQLite")
elif url.startswith("postgresql://") or url.startswith("postgresql+"):
    print("DATABASE TYPE: PostgreSQL")
elif url:
    print("DATABASE TYPE: Other URL scheme — value hidden")
else:
    print("DATABASE TYPE: Missing or empty")
