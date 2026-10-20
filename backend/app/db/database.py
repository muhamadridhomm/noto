import aiosqlite
import sqlite3
from pathlib import Path
from ..core.config import settings

def get_db_path() -> Path:
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    return settings.DATABASE_PATH

async def get_db():
    db = await aiosqlite.connect(get_db_path())
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA foreign_keys = ON;")
    await db.execute("PRAGMA journal_mode = WAL;")
    try:
        yield db
    finally:
        await db.close()

async def init_db():
    """Initializes tables and FTS5 search indexing triggers."""
    db_path = get_db_path()
    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        await db.execute("PRAGMA journal_mode = WAL;")
        
        # Folders Table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS folders (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            icon TEXT DEFAULT 'folder',
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Notes Table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            folder_id TEXT REFERENCES folders(id) ON DELETE SET NULL,
            title TEXT NOT NULL,
            content TEXT DEFAULT '',
            is_pinned BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # FTS5 Virtual Table for full-text search
        await db.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
            note_id UNINDEXED,
            title,
            content,
            tokenize = 'porter unicode61'
        );
        """)

        # Triggers to keep FTS5 synchronized with notes
        await db.execute("""
        CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
            INSERT INTO notes_fts(note_id, title, content)
            VALUES (new.id, new.title, new.content);
        END;
        """)

        await db.execute("""
        CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN
            DELETE FROM notes_fts WHERE note_id = old.id;
        END;
        """)

        await db.execute("""
        CREATE TRIGGER IF NOT EXISTS notes_au AFTER UPDATE ON notes BEGIN
            DELETE FROM notes_fts WHERE note_id = old.id;
            INSERT INTO notes_fts(note_id, title, content)
            VALUES (new.id, new.title, new.content);
        END;
        """)

        # Default folder if none exists
        cursor = await db.execute("SELECT COUNT(*) FROM folders")
        count = (await cursor.fetchone())[0]
        if count == 0:
            await db.execute("""
            INSERT INTO folders (id, name, icon, sort_order)
            VALUES ('default-notes', 'General Notes', 'book-open', 0);
            """)
            await db.execute("""
            INSERT INTO notes (id, folder_id, title, content, is_pinned)
            VALUES (
                'welcome-note',
                'default-notes',
                'Welcome to Noto 👋',
                '# Welcome to Noto\n\nNoto is your local-first, AI-assisted note workspace.\n\n### How it works:\n1. **Capture & Write**: Create notes in folders on the left sidebar.\n2. **AI Copilot (Ctrl+J)**: Ask the AI to draft new notes from rough ideas or tidy what you have written.\n3. **Review & Approve**: The AI will never silently alter your notes. Inspect the draft, edit it if you like, and choose where to save it.\n4. **Instant Search (Ctrl+K)**: Search across all your notes locally.\n\nEverything stays private on your computer!',
                1
            );
            """)

        await db.commit()
