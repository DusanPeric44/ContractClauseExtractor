import aiosqlite
from dotenv import load_dotenv
import os

def get_db_path():
    load_dotenv()
    db_path = os.getenv('DB_PATH')
    if not db_path:
        raise ValueError('DB_PATH environment variable is not set')
    return db_path

async def create_database() -> None:
    async with aiosqlite.connect(get_db_path()) as db:
        await db.execute('PRAGMA foreign_keys = ON')
        await db.execute(
            '''
            CREATE TABLE IF NOT EXISTS document (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                text TEXT NOT NULL
            )
            '''
        )
        await db.execute(
            '''
            CREATE TABLE IF NOT EXISTS extraction (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                FOREIGN KEY(document_id) REFERENCES document(id) ON DELETE CASCADE
            )
            '''
        )
        await db.execute(
            '''
            CREATE TABLE IF NOT EXISTS clause (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                text TEXT NOT NULL,
                start INTEGER NOT NULL,
                end INTEGER NOT NULL,
                extraction_id INTEGER NOT NULL,
                FOREIGN KEY(extraction_id) REFERENCES extraction(id) ON DELETE CASCADE
            )
            '''
        )
        await db.execute(
            '''
            CREATE TABLE IF NOT EXISTS metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parties TEXT,
                effective_date TEXT,
                termination TEXT,
                governing_law TEXT,
                jurisdiction TEXT,
                payment_terms TEXT,
                renewal TEXT,
                confidentiality TEXT,
                liability_limit TEXT,
                extraction_id INTEGER NOT NULL,
                FOREIGN KEY(extraction_id) REFERENCES extraction(id) ON DELETE CASCADE
            )
            '''
        )
        await db.execute('CREATE INDEX IF NOT EXISTS idx_extraction_document_id ON extraction(document_id)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_clause_extraction_id ON clause(extraction_id)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_metadata_extraction_id ON metadata(extraction_id)')
        await db.commit()