import asyncio
import os
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv
from libsql_client import create_client

load_dotenv(Path("backend/.env"), override=True)

original_url = os.getenv("TURSO_DATABASE_URL", "")
token = os.getenv("TURSO_AUTH_TOKEN", "")

if not original_url or not token:
    print("RESULT: URL or token missing")
    raise SystemExit(1)

host = urlparse(original_url).hostname
https_url = "https://" + host

async def main():
    try:
        async with create_client(url=https_url, auth_token=token) as client:
            await client.execute("SELECT 1")
            print("RESULT: HTTPS TURSO CONNECTION OK")
    except Exception as exc:
        print("RESULT: HTTPS CONNECTION FAILED")
        print("ERROR TYPE:", type(exc).__name__)
        print("ERROR:", str(exc)[:300])

asyncio.run(main())
