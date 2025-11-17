import aiosqlite
from typing import List
from models.clause import ClauseBase
from database import get_db_path


async def insert_many(clauses: List[ClauseBase]) -> None:
    if not clauses:
        return
    async with aiosqlite.connect(get_db_path()) as db:
        await db.execute('PRAGMA foreign_keys = ON')
        await db.executemany(
            'INSERT INTO clause (name, text, start, end, extraction_id) VALUES (?, ?, ?, ?, ?)',
            [
                (c.name, c.text, c.start, c.end, c.extraction_id)
                for c in clauses
            ],
        )
        await db.commit()


async def get_by_extraction_id(extraction_id: int):
    async with aiosqlite.connect(get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        await db.execute('PRAGMA foreign_keys = ON')
        cur = await db.execute(
            'SELECT id, name, text, start, end, extraction_id FROM clause WHERE extraction_id = ? ORDER BY start ASC',
            (extraction_id,),
        )
        rows = await cur.fetchall()
        return [dict(row) for row in rows]