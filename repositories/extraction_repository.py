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


async def get_by_document_id(document_id: int):
    async with aiosqlite.connect(get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        await db.execute('PRAGMA foreign_keys = ON')
        cur = await db.execute(
            'SELECT id FROM extraction WHERE document_id = ? ORDER BY id DESC',
            (document_id,),
        )
        rows = await cur.fetchall()
        return [tuple(row) for row in rows]


async def list(pageNum: int, pageSize: int):
    offset = max(pageNum - 1, 0) * pageSize
    async with aiosqlite.connect(get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        await db.execute('PRAGMA foreign_keys = ON')
        cur = await db.execute(
            'SELECT id, document_id FROM extraction ORDER BY id DESC LIMIT ? OFFSET ?',
            (pageSize, offset),
        )
        rows = await cur.fetchall()
        return [tuple(row) for row in rows]