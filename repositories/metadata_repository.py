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