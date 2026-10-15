import sqlite3
from pathlib import Path

path = Path("backend/instance/local.db").resolve()
connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)

try:
    print("--- CATEGORIES ---")
    for row in connection.execute("""
        SELECT id, slug, name_en, name_ne, is_active
        FROM categories ORDER BY sort_order, id
    """):
        print(row)

    print("\n--- FOOD ITEMS ---")
    for row in connection.execute("""
        SELECT id, category_id, slug, name_en, base_price, is_published
        FROM food_items ORDER BY sort_order, id
    """):
        print(row)

    print("\n--- FOREIGN KEY CHECK ---")
    missing = connection.execute("""
        SELECT f.id, f.category_id, f.name_en
        FROM food_items f
        LEFT JOIN categories c ON c.id = f.category_id
        WHERE c.id IS NULL
    """).fetchall()
    print("FOOD ITEMS WITH MISSING CATEGORY:", missing)
finally:
    connection.close()
