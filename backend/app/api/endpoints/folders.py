import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
import aiosqlite
from ...db.database import get_db
from ...models.schemas import FolderCreate, FolderUpdate, FolderResponse

router = APIRouter(prefix="/folders", tags=["folders"])

@router.get("", response_model=List[FolderResponse])
async def list_folders(db: aiosqlite.Connection = Depends(get_db)):
    query = """
    SELECT f.id, f.name, f.icon, f.sort_order, f.created_at, f.updated_at,
           COUNT(n.id) as note_count
    FROM folders f
    LEFT JOIN notes n ON f.id = n.folder_id
    GROUP BY f.id
    ORDER BY f.sort_order ASC, f.created_at ASC
    """
    cursor = await db.execute(query)
    rows = await cursor.fetchall()
    return [
        FolderResponse(
            id=row["id"],
            name=row["name"],
            icon=row["icon"],
            sort_order=row["sort_order"],
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
            note_count=row["note_count"]
        )
        for row in rows
    ]

@router.post("", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(folder: FolderCreate, db: aiosqlite.Connection = Depends(get_db)):
    folder_id = f"folder-{uuid.uuid4().hex[:10]}"
    await db.execute(
        "INSERT INTO folders (id, name, icon, sort_order) VALUES (?, ?, ?, ?)",
        (folder_id, folder.name.strip(), folder.icon or "folder", folder.sort_order or 0)
    )
    await db.commit()
    
    cursor = await db.execute("SELECT * FROM folders WHERE id = ?", (folder_id,))
    row = await cursor.fetchone()
    return FolderResponse(
        id=row["id"],
        name=row["name"],
        icon=row["icon"],
        sort_order=row["sort_order"],
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
        note_count=0
    )

@router.put("/{folder_id}", response_model=FolderResponse)
async def update_folder(folder_id: str, updates: FolderUpdate, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM folders WHERE id = ?", (folder_id,))
    existing = await cursor.fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Folder not found")
        
    name = updates.name.strip() if updates.name is not None else existing["name"]
    icon = updates.icon if updates.icon is not None else existing["icon"]
    sort_order = updates.sort_order if updates.sort_order is not None else existing["sort_order"]
    
    await db.execute(
        "UPDATE folders SET name = ?, icon = ?, sort_order = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (name, icon, sort_order, folder_id)
    )
    await db.commit()
    
    cursor = await db.execute("""
        SELECT f.*, COUNT(n.id) as note_count
        FROM folders f
        LEFT JOIN notes n ON f.id = n.folder_id
        WHERE f.id = ?
        GROUP BY f.id
    """, (folder_id,))
    row = await cursor.fetchone()
    return FolderResponse(
        id=row["id"],
        name=row["name"],
        icon=row["icon"],
        sort_order=row["sort_order"],
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
        note_count=row["note_count"]
    )

@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(folder_id: str, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM folders WHERE id = ?", (folder_id,))
    existing = await cursor.fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Set folder_id = NULL for associated notes, then delete folder
    await db.execute("UPDATE notes SET folder_id = NULL WHERE folder_id = ?", (folder_id,))
    await db.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
    await db.commit()
    return None
