import re
from typing import List
from fastapi import APIRouter, Depends, Query
import aiosqlite
from ...db.database import get_db
from ...models.schemas import SearchResult

router = APIRouter(prefix="/search", tags=["search"])

def sanitize_fts_query(term: str) -> str:
    # Remove FTS special operator chars and extract words
    words = re.findall(r'\w+', term)
    if not words:
        return ""
    # Search each word prefix
    return " ".join([f'"{w}"*' for w in words])

@router.get("", response_model=List[SearchResult])
async def search_notes(
    q: str = Query(..., min_length=1),
    db: aiosqlite.Connection = Depends(get_db)
):
    clean_q = sanitize_fts_query(q)
    if not clean_q:
        return []

    query = """
    SELECT 
        n.id, 
        n.title, 
        n.folder_id,
        f.name as folder_name,
        n.updated_at,
        snippet(notes_fts, 2, '<mark class="bg-amber-200 dark:bg-amber-800 text-inherit px-0.5 rounded">', '</mark>', '...', 15) as snippet
    FROM notes_fts fts
    JOIN notes n ON fts.note_id = n.id
    LEFT JOIN folders f ON n.folder_id = f.id
    WHERE notes_fts MATCH ?
    ORDER BY rank
    LIMIT 25;
    """
    
    try:
        cursor = await db.execute(query, (clean_q,))
        rows = await cursor.fetchall()
        return [
            SearchResult(
                id=row["id"],
                title=row["title"],
                snippet=row["snippet"] or "",
                folder_id=row["folder_id"],
                folder_name=row["folder_name"] or "General",
                updated_at=str(row["updated_at"])
            )
            for row in rows
        ]
    except Exception:
        # Fallback to simple LIKE if FTS fails on strange syntax
        like_query = """
        SELECT n.id, n.title, n.folder_id, f.name as folder_name, n.updated_at,
               SUBSTR(n.content, 1, 100) as snippet
        FROM notes n
        LEFT JOIN folders f ON n.folder_id = f.id
        WHERE n.title LIKE ? OR n.content LIKE ?
        LIMIT 25;
        """
        like_term = f"%{q}%"
        cursor = await db.execute(like_query, (like_term, like_term))
        rows = await cursor.fetchall()
        return [
            SearchResult(
                id=row["id"],
                title=row["title"],
                snippet=row["snippet"] or "",
                folder_id=row["folder_id"],
                folder_name=row["folder_name"] or "General",
                updated_at=str(row["updated_at"])
            )
            for row in rows
        ]
