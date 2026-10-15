import sys
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path("backend").resolve()))

from app import create_app
from app.config import Config
from app.extensions import db

class SafeTestConfig(Config):
    ADMIN_BOOTSTRAP_ENABLED = False

app = create_app(SafeTestConfig)

with app.app_context():
    with db.engine.connect() as connection:
        for table in ("categories", "food_items"):
            count = connection.execute(
                text(f'SELECT COUNT(*) FROM "{table}"')
            ).scalar_one()
            print(f"TURSO {table.upper()} COUNT:", count)

    client = app.test_client()
    for endpoint in (
        "/health",
        "/api/v1/menu/categories?lang=en",
    ):
        response = client.get(endpoint)
        print(f"\nGET {endpoint}")
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.get_data(as_text=True)[:700])
