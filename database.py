
import sqlite3
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "palettes.db"


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS palettes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                colors TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_palette(name, colors):
    if not name.strip():
        raise ValueError("Please enter a palette name.")

    colors_json = json.dumps(colors)

    with get_connection() as connection:
        connection.execute(
            "INSERT INTO palettes (name, colors) VALUES (?, ?)",
            (name.strip(), colors_json)
        )


def get_saved_palettes():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT id, name, colors, created_at
            FROM palettes
            ORDER BY id DESC
        """).fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "colors": json.loads(row[2]),
            "created_at": row[3]
        }
        for row in rows
    ]


def delete_palette(palette_id):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM palettes WHERE id = ?",
            (palette_id,)
        )
