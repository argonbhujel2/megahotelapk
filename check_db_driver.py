from sqlalchemy import create_engine

urls = [
    "sqlite:///driver_test.db",
    "sqlite+libsql://example.turso.io?secure=true",
]

for url in urls:
    try:
        engine = create_engine(url)
        print(url.split("://")[0] + ": URL accepted")
        engine.dispose()
    except Exception as exc:
        print(url.split("://")[0] + ": " + type(exc).__name__ + ": " + str(exc)[:250])
