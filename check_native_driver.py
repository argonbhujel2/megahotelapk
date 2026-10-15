from sqlalchemy import create_engine
import sqlalchemy_libsql_native

print("NATIVE DRIVER IMPORT: OK")
print("MODULE:", sqlalchemy_libsql_native.__file__)

for url in [
    "sqlite+libsql://example.turso.io?secure=true",
    "sqlite+libsql_native://example.turso.io",
]:
    try:
        engine = create_engine(url)
        print(url.split("://")[0] + ": URL accepted")
        engine.dispose()
    except Exception as exc:
        print(url.split("://")[0] + ":", type(exc).__name__, str(exc)[:200])
