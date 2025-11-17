import aiosqlite
from models.document import DocumentBase
from database import get_db_path


async def insert(document: DocumentBase) -> int:
    async with aiosqlite.connect(get_db_path()) as db:
        await db.execute('PRAGMA foreign_keys = ON')
        cursor = await db.execute(
            'INSERT INTO document (name, text) VALUES (?, ?)',
            (document.name, document.text),
        )
        await db.commit()
        return cursor.lastrowid