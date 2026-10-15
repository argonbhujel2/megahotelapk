import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from libsql_client import create_client

load_dotenv(Path("backend/.env"), override=True)

url = os.getenv("TURSO_DATABASE_URL")
token = os.getenv("TURSO_AUTH_TOKEN")

if not url or not token:
    print("RESULT: Turso URL or token is missing")
    raise SystemExit(1)

async def main():
    client = None
    try:
        client = create_client(url=url, auth_token=token)
        result = await client.execute("SELECT 1")
        print("RESULT: TURSO CONNECTION OK")
        print("QUERY EXECUTED: SELECT 1")
    except Exception as exc:
        print("RESULT: CONNECTION FAILED")
        print("ERROR TYPE:", type(exc).__name__)
        print("ERROR:", str(exc)[:350])
    finally:
        if client is not None:
            await client.close()

asyncio.run(main())
