from importlib.metadata import entry_points, version, PackageNotFoundError

for package in ("sqlalchemy-libsql", "sqlalchemy-libsql-native", "libsql", "libsql-client"):
    try:
        print(f"{package}: {version(package)}")
    except PackageNotFoundError:
        print(f"{package}: NOT INSTALLED")

print("\nSQLAlchemy dialect registrations:")
for ep in entry_points(group="sqlalchemy.dialects"):
    if "libsql" in ep.name.lower() or "libsql" in ep.value.lower():
        print(f"{ep.name} -> {ep.value}")
