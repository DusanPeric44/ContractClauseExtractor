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