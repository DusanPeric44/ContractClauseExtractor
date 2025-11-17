import aiosqlite
from database import get_db_path


async def insert(document_id: int) -> int:
    async with aiosqlite.connect(get_db_path()) as db:
        await db.execute('PRAGMA foreign_keys = ON')
        cursor = await db.execute(
            'INSERT INTO extraction (document_id) VALUES (?)',
            (document_id,),
        )
        await db.commit()
        return cursor.lastrowid