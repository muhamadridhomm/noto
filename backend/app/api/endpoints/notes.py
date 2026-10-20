import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
import aiosqlite
from ...db.database import get_db
from ...models.schemas import NoteCreate, NoteUpdate, NoteResponse

router = APIRouter(prefix="/notes", tags=["notes"])

@router.get("", response_model=List[NoteResponse])
async def list_notes(
    folder_id: Optional[str] = Query(None),
    is_pinned: Optional[bool] = Query(None),
    db: aiosqlite.Connection = Depends(get_db)
):
    conditions = []
    params = []
    
    if folder_id is not None:
        if folder_id == "uncategorized":
            conditions.append("folder_id IS NULL")
        else:
            conditions.append("folder_id = ?")
            params.append(folder_id)
            
    if is_pinned is not None:
        conditions.append("is_pinned = ?")
        params.append(1 if is_pinned else 0)
        
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"""
    SELECT id, folder_id, title, content, is_pinned, created_at, updated_at
    FROM notes
    {where_clause}
    ORDER BY is_pinned DESC, updated_at DESC
    """
    
    cursor = await db.execute(query, tuple(params))
    rows = await cursor.fetchall()
    return [
        NoteResponse(
            id=row["id"],
            folder_id=row["folder_id"],
            title=row["title"],
            content=row["content"],
            is_pinned=bool(row["is_pinned"]),
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"])
        )
        for row in rows
    ]

@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")
        
    return NoteResponse(
        id=row["id"],
        folder_id=row["folder_id"],
        title=row["title"],
        content=row["content"],
        is_pinned=bool(row["is_pinned"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"])
    )

@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(note: NoteCreate, db: aiosqlite.Connection = Depends(get_db)):
    note_id = f"note-{uuid.uuid4().hex[:10]}"
    
    # If folder_id provided, verify folder exists
    if note.folder_id:
        c = await db.execute("SELECT id FROM folders WHERE id = ?", (note.folder_id,))
        if not await c.fetchone():
            note.folder_id = None
            
    await db.execute("""
        INSERT INTO notes (id, folder_id, title, content, is_pinned)
        VALUES (?, ?, ?, ?, ?)
    """, (
        note_id,
        note.folder_id,
        note.title.strip() or "Untitled Note",
        note.content or "",
        1 if note.is_pinned else 0
    ))
    await db.commit()
    
    cursor = await db.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = await cursor.fetchone()
    return NoteResponse(
        id=row["id"],
        folder_id=row["folder_id"],
        title=row["title"],
        content=row["content"],
        is_pinned=bool(row["is_pinned"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"])
    )

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, updates: NoteUpdate, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    existing = await cursor.fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Note not found")
        
    title = updates.title.strip() if updates.title is not None else existing["title"]
    content = updates.content if updates.content is not None else existing["content"]
    folder_id = updates.folder_id if updates.folder_id is not None else existing["folder_id"]
    is_pinned = (1 if updates.is_pinned else 0) if updates.is_pinned is not None else existing["is_pinned"]
    
    if folder_id:
        c = await db.execute("SELECT id FROM folders WHERE id = ?", (folder_id,))
        if not await c.fetchone():
            folder_id = None

    await db.execute("""
        UPDATE notes 
        SET title = ?, content = ?, folder_id = ?, is_pinned = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (title, content, folder_id, is_pinned, note_id))
    await db.commit()
    
    cursor = await db.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = await cursor.fetchone()
    return NoteResponse(
        id=row["id"],
        folder_id=row["folder_id"],
        title=row["title"],
        content=row["content"],
        is_pinned=bool(row["is_pinned"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"])
    )

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: str, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
    if not await cursor.fetchone():
        raise HTTPException(status_code=404, detail="Note not found")
        
    await db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    await db.commit()
    return None
