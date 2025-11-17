import aiosqlite
import json
from models.metadata import MetadataBase
from database import get_db_path


async def insert(metadata: MetadataBase) -> int:
    async with aiosqlite.connect(get_db_path()) as db:
        await db.execute('PRAGMA foreign_keys = ON')
        cursor = await db.execute(
            'INSERT INTO metadata (parties, effective_date, termination, governing_law, jurisdiction, payment_terms, renewal, confidentiality, liability_limit, extraction_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                json.dumps(metadata.parties or []),
                metadata.effective_date,
                metadata.termination,
                metadata.governing_law,
                metadata.jurisdiction,
                metadata.payment_terms,
                metadata.renewal,
                metadata.confidentiality,
                metadata.liability_limit,
                metadata.extraction_id,
            ),
        )
        await db.commit()
        return cursor.lastrowid


async def get_by_extraction_id(extraction_id: int):
    async with aiosqlite.connect(get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        await db.execute('PRAGMA foreign_keys = ON')
        cur = await db.execute(
            'SELECT id, parties, effective_date, termination, governing_law, jurisdiction, payment_terms, renewal, confidentiality, liability_limit, extraction_id FROM metadata WHERE extraction_id = ? LIMIT 1',
            (extraction_id,),
        )
        row = await cur.fetchone()
        if not row:
            return None
        d = dict(row)
        try:
            d['parties'] = json.loads(d['parties']) if d['parties'] else []
        except Exception:
            d['parties'] = []
        return d