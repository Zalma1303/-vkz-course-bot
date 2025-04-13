# db.py

import aiosqlite
from datetime import datetime

DB_NAME = "db.sqlite3"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                user_id INTEGER,
                username TEXT,
                course TEXT,
                lang TEXT,
                date TEXT,
                confirmed_by TEXT
            )
        ''')
        await db.commit()


async def log_purchase(user_id: int, username: str, course: str, lang: str, confirmed_by: str):
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO purchases (user_id, username, course, lang, date, confirmed_by) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, course, lang, date, confirmed_by)
        )
        await db.commit()