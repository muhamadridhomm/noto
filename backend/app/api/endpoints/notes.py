import json
import re
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
import aiosqlite
from ...db.database import get_db
from ...models.schemas import (
    NoteCreate,
    NoteUpdate,
    NoteResponse,
    NoteHistoryResponse,
    GlobalTaskItem,
    GlobalTargetItem,
    TargetCreate,
    TargetUpdate,
    TaskUpdate,
    TaskCreate
)

router = APIRouter(prefix="/notes", tags=["notes"])
TASKS_REGEX = re.compile(r"```tasks\s*([\s\S]*?)\s*```")

@router.get("", response_model=List[NoteResponse])
async def list_notes(
    folder_id: Optional[str] = Query(None),
    is_pinned: Optional[bool] = Query(None),
    include_deleted: bool = Query(False),
    db: aiosqlite.Connection = Depends(get_db)
):
    conditions = []
    params = []

    if not include_deleted:
        conditions.append("(is_deleted = 0 OR is_deleted IS NULL)")

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
    SELECT id, folder_id, title, content, is_pinned, is_deleted, created_at, updated_at
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
            is_deleted=bool(row["is_deleted"]) if "is_deleted" in row.keys() else False,
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"])
        )
        for row in rows
    ]

# --- Trash Endpoints ---

@router.get("/trash", response_model=List[NoteResponse])
async def list_trash_notes(db: aiosqlite.Connection = Depends(get_db)):
    query = """
    SELECT id, folder_id, title, content, is_pinned, is_deleted, created_at, updated_at
    FROM notes
    WHERE is_deleted = 1
    ORDER BY updated_at DESC
    """
    cursor = await db.execute(query)
    rows = await cursor.fetchall()
    return [
        NoteResponse(
            id=row["id"],
            folder_id=row["folder_id"],
            title=row["title"],
            content=row["content"],
            is_pinned=bool(row["is_pinned"]),
            is_deleted=True,
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"])
        )
        for row in rows
    ]

@router.post("/empty-trash")
async def empty_trash(db: aiosqlite.Connection = Depends(get_db)):
    await db.execute("DELETE FROM notes WHERE is_deleted = 1")
    await db.commit()
    return {"message": "Trash emptied successfully"}

@router.post("/{note_id}/restore", response_model=NoteResponse)
async def restore_note(note_id: str, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    existing = await cursor.fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Note not found")

    await db.execute("UPDATE notes SET is_deleted = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (note_id,))
    await db.commit()

    c = await db.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = await c.fetchone()
    return NoteResponse(
        id=row["id"],
        folder_id=row["folder_id"],
        title=row["title"],
        content=row["content"],
        is_pinned=bool(row["is_pinned"]),
        is_deleted=False,
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"])
    )

# --- Global Master Tasks & Targets Aggregator ---

@router.get("/tasks/all", response_model=List[GlobalTaskItem])
async def list_all_tasks(db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("""
        SELECT n.id, n.title, n.content, n.folder_id, f.name as folder_name
        FROM notes n
        LEFT JOIN folders f ON n.folder_id = f.id
        WHERE (n.is_deleted = 0 OR n.is_deleted IS NULL) AND n.content LIKE '%```tasks%'
        ORDER BY n.updated_at DESC
    """)
    rows = await cursor.fetchall()
    all_tasks = []

    for row in rows:
        note_id = row["id"]
        note_title = row["title"]
        folder_id = row["folder_id"]
        folder_name = row["folder_name"] or "Uncategorized"
        content = row["content"]
        match = TASKS_REGEX.search(content)
        if match:
            try:
                tasks_data = json.loads(match.group(1))
                task_list = []
                if isinstance(tasks_data, list):
                    task_list = tasks_data
                elif isinstance(tasks_data, dict):
                    task_list = tasks_data.get("tasks", [])

                for t in task_list:
                    all_tasks.append(GlobalTaskItem(
                        id=t.get("id", f"task-{uuid.uuid4().hex[:6]}"),
                        note_id=note_id,
                        note_title=note_title,
                        folder_id=folder_id,
                        folder_name=folder_name,
                        title=t.get("title", ""),
                        done=bool(t.get("done", False)),
                        status=t.get("status", "To Do"),
                        priority=t.get("priority", "Normal"),
                        due_date=t.get("due_date", ""),
                        group=t.get("group", ""),
                        notes=t.get("notes") or t.get("description") or ""
                    ))
            except Exception:
                continue

    # Sort tasks: Urgent first, then High, then Normal, then Low, then Done last
    priority_weight = {"Urgent": 0, "High": 1, "Normal": 2, "Low": 3}
    all_tasks.sort(key=lambda t: (1 if t.done else 0, priority_weight.get(t.priority, 2)))
    return all_tasks

@router.get("/targets/all", response_model=List[GlobalTargetItem])
async def list_all_targets(db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("""
        SELECT n.id, n.title, n.content, n.folder_id, f.name as folder_name
        FROM notes n
        LEFT JOIN folders f ON n.folder_id = f.id
        WHERE (n.is_deleted = 0 OR n.is_deleted IS NULL) AND n.content LIKE '%```tasks%'
        ORDER BY n.updated_at DESC
    """)
    rows = await cursor.fetchall()
    all_targets = []

    for row in rows:
        note_id = row["id"]
        note_title = row["title"]
        folder_id = row["folder_id"]
        folder_name = row["folder_name"] or "Uncategorized"
        content = row["content"]
        match = TASKS_REGEX.search(content)
        if match:
            try:
                data = json.loads(match.group(1))
                if isinstance(data, dict) and "targets" in data and isinstance(data["targets"], list):
                    for tgt in data["targets"]:
                        all_targets.append(GlobalTargetItem(
                            id=tgt.get("id", f"tgt-{uuid.uuid4().hex[:6]}"),
                            note_id=note_id,
                            note_title=note_title,
                            folder_id=folder_id,
                            folder_name=folder_name,
                            title=tgt.get("title", ""),
                            badge=tgt.get("badge", ""),
                            date=tgt.get("date", ""),
                            description=tgt.get("description", "")
                        ))
            except Exception:
                continue

    return all_targets


def extract_or_init_task_data(content: str):
    match = TASKS_REGEX.search(content or "")
    if not match:
        return {"tasks": [], "targets": [], "groups": []}, None
    raw = match.group(1).strip()
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return {"tasks": parsed, "targets": [], "groups": []}, match
        elif isinstance(parsed, dict):
            return {
                "tasks": parsed.get("tasks", []),
                "targets": parsed.get("targets", []),
                "groups": parsed.get("groups", [])
            }, match
    except Exception:
        pass
    return {"tasks": [], "targets": [], "groups": []}, match


def serialize_task_data_into_content(content: str, data: dict, match=None) -> str:
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    block = f"```tasks\n{json_str}\n```"
    if match:
        return content[:match.start()] + block + content[match.end():]
    else:
        clean = (content or "").rstrip()
        return (clean + "\n\n" + block + "\n") if clean else (block + "\n")


# --- Note Targets & Tasks Direct CRUD Endpoints ---

@router.post("/{note_id}/targets")
async def add_target_to_note(
    note_id: str,
    target_data: TargetCreate,
    db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.execute("SELECT id, content FROM notes WHERE id = ?", (note_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")
    content = row["content"] or ""
    data, match = extract_or_init_task_data(content)

    new_tgt = {
        "id": f"tgt-{uuid.uuid4().hex[:8]}",
        "title": target_data.title.strip(),
        "badge": target_data.badge.strip() if target_data.badge else "Milestone",
        "date": target_data.date.strip() if target_data.date else "",
        "description": target_data.description.strip() if target_data.description else ""
    }
    data["targets"].append(new_tgt)
    new_content = serialize_task_data_into_content(content, data, match)
    await db.execute(
        "UPDATE notes SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_content, note_id)
    )
    await db.commit()
    return new_tgt


@router.put("/{note_id}/targets/{target_id}")
async def update_target_in_note(
    note_id: str,
    target_id: str,
    updates: TargetUpdate,
    db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.execute("SELECT id, content FROM notes WHERE id = ?", (note_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")
    content = row["content"] or ""
    data, match = extract_or_init_task_data(content)

    found = None
    for tgt in data["targets"]:
        if tgt.get("id") == target_id:
            found = tgt
            break
    if not found:
        raise HTTPException(status_code=404, detail="Target not found in note")

    if updates.title is not None:
        found["title"] = updates.title.strip()
    if updates.badge is not None:
        found["badge"] = updates.badge.strip()
    if updates.date is not None:
        found["date"] = updates.date.strip()
    if updates.description is not None:
        found["description"] = updates.description.strip()

    new_content = serialize_task_data_into_content(content, data, match)
    await db.execute(
        "UPDATE notes SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_content, note_id)
    )
    await db.commit()
    return found


@router.delete("/{note_id}/targets/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_target_from_note(
    note_id: str,
    target_id: str,
    db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.execute("SELECT id, content FROM notes WHERE id = ?", (note_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")
    content = row["content"] or ""
    data, match = extract_or_init_task_data(content)

    orig_len = len(data["targets"])
    data["targets"] = [tgt for tgt in data["targets"] if tgt.get("id") != target_id]
    if len(data["targets"]) == orig_len:
        raise HTTPException(status_code=404, detail="Target not found in note")

    new_content = serialize_task_data_into_content(content, data, match)
    await db.execute(
        "UPDATE notes SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_content, note_id)
    )
    await db.commit()
    return None


@router.patch("/{note_id}/tasks/{task_id}")
async def patch_task_in_note(
    note_id: str,
    task_id: str,
    updates: TaskUpdate,
    db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.execute("SELECT id, content FROM notes WHERE id = ?", (note_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")
    content = row["content"] or ""
    data, match = extract_or_init_task_data(content)

    found = None
    for t in data["tasks"]:
        if t.get("id") == task_id:
            found = t
            break
    if not found:
        raise HTTPException(status_code=404, detail="Task not found in note")

    if updates.title is not None:
        found["title"] = updates.title.strip()
    if updates.done is not None:
        found["done"] = updates.done
        if updates.done and found.get("status") != "Done":
            found["status"] = "Done"
        elif not updates.done and found.get("status") == "Done":
            found["status"] = "To Do"
    if updates.status is not None:
        found["status"] = updates.status
        found["done"] = (updates.status == "Done")
    if updates.priority is not None:
        found["priority"] = updates.priority
    if updates.due_date is not None:
        found["due_date"] = updates.due_date
    if updates.group is not None:
        found["group"] = updates.group
    if updates.notes is not None:
        found["notes"] = updates.notes

    new_content = serialize_task_data_into_content(content, data, match)
    await db.execute(
        "UPDATE notes SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_content, note_id)
    )
    await db.commit()
    return found


@router.post("/{note_id}/tasks")
async def add_task_to_note(
    note_id: str,
    task_data: TaskCreate,
    db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.execute("SELECT id, content FROM notes WHERE id = ?", (note_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")
    content = row["content"] or ""
    data, match = extract_or_init_task_data(content)

    new_task = {
        "id": f"task-{uuid.uuid4().hex[:8]}",
        "title": task_data.title.strip(),
        "done": False,
        "status": task_data.status or "To Do",
        "priority": task_data.priority or "Normal",
        "due_date": task_data.due_date or "",
        "group": task_data.group or "",
        "notes": task_data.notes or ""
    }
    if new_task["status"] == "Done":
        new_task["done"] = True
    data["tasks"].append(new_task)
    new_content = serialize_task_data_into_content(content, data, match)
    await db.execute(
        "UPDATE notes SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_content, note_id)
    )
    await db.commit()
    return new_task


@router.delete("/{note_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_from_note(
    note_id: str,
    task_id: str,
    db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.execute("SELECT id, content FROM notes WHERE id = ?", (note_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")
    content = row["content"] or ""
    data, match = extract_or_init_task_data(content)

    orig_len = len(data["tasks"])
    data["tasks"] = [t for t in data["tasks"] if t.get("id") != task_id]
    if len(data["tasks"]) == orig_len:
        raise HTTPException(status_code=404, detail="Task not found in note")

    new_content = serialize_task_data_into_content(content, data, match)
    await db.execute(
        "UPDATE notes SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_content, note_id)
    )
    await db.commit()
    return None

# --- Individual Note Operations ---

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
        is_deleted=bool(row["is_deleted"]) if "is_deleted" in row.keys() else False,
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"])
    )

@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(note: NoteCreate, db: aiosqlite.Connection = Depends(get_db)):
    note_id = f"note-{uuid.uuid4().hex[:10]}"

    if note.folder_id:
        c = await db.execute("SELECT id FROM folders WHERE id = ?", (note.folder_id,))
        if not await c.fetchone():
            note.folder_id = None

    await db.execute("""
        INSERT INTO notes (id, folder_id, title, content, is_pinned, is_deleted)
        VALUES (?, ?, ?, ?, ?, 0)
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
        is_deleted=False,
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"])
    )

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, updates: NoteUpdate, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    existing = await cursor.fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Note not found")

    old_title = existing["title"]
    old_content = existing["content"]
    title = updates.title.strip() if updates.title is not None else old_title
    content = updates.content if updates.content is not None else old_content
    folder_id = updates.folder_id if updates.folder_id is not None else existing["folder_id"]
    is_pinned = (1 if updates.is_pinned else 0) if updates.is_pinned is not None else existing["is_pinned"]
    is_deleted = (1 if updates.is_deleted else 0) if updates.is_deleted is not None else existing["is_deleted"]

    if folder_id:
        c = await db.execute("SELECT id FROM folders WHERE id = ?", (folder_id,))
        if not await c.fetchone():
            folder_id = None

    # Snapshot to note_history if content changed meaningfully (more than 10 characters difference)
    if content and content != old_content and abs(len(content) - len(old_content)) >= 10:
        hist_id = f"hist-{uuid.uuid4().hex[:8]}"
        await db.execute("""
            INSERT INTO note_history (id, note_id, title, content)
            VALUES (?, ?, ?, ?)
        """, (hist_id, note_id, old_title, old_content))

        # Keep at most 25 latest snapshots per note
        await db.execute("""
            DELETE FROM note_history
            WHERE note_id = ? AND id NOT IN (
                SELECT id FROM note_history WHERE note_id = ? ORDER BY created_at DESC LIMIT 25
            )
        """, (note_id, note_id))

    await db.execute("""
        UPDATE notes
        SET title = ?, content = ?, folder_id = ?, is_pinned = ?, is_deleted = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (title, content, folder_id, is_pinned, is_deleted, note_id))
    await db.commit()

    cursor = await db.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = await cursor.fetchone()
    return NoteResponse(
        id=row["id"],
        folder_id=row["folder_id"],
        title=row["title"],
        content=row["content"],
        is_pinned=bool(row["is_pinned"]),
        is_deleted=bool(row["is_deleted"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"])
    )

# Soft delete (moves to trash)
@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: str, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
    if not await cursor.fetchone():
        raise HTTPException(status_code=404, detail="Note not found")

    await db.execute("UPDATE notes SET is_deleted = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (note_id,))
    await db.commit()
    return None

# Permanent deletion
@router.delete("/{note_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
async def permanent_delete_note(note_id: str, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
    if not await cursor.fetchone():
        raise HTTPException(status_code=404, detail="Note not found")

    await db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    await db.execute("DELETE FROM note_history WHERE note_id = ?", (note_id,))
    await db.commit()
    return None

# --- Version History (Time Machine) Endpoints ---

@router.get("/{note_id}/history", response_model=List[NoteHistoryResponse])
async def get_note_history(note_id: str, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("""
        SELECT id, note_id, title, content, created_at
        FROM note_history
        WHERE note_id = ?
        ORDER BY created_at DESC
    """, (note_id,))
    rows = await cursor.fetchall()
    return [
        NoteHistoryResponse(
            id=row["id"],
            note_id=row["note_id"],
            title=row["title"],
            content=row["content"],
            created_at=str(row["created_at"])
        )
        for row in rows
    ]

@router.post("/{note_id}/restore-history/{history_id}", response_model=NoteResponse)
async def restore_note_history(note_id: str, history_id: str, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM note_history WHERE id = ? AND note_id = ?", (history_id, note_id))
    hist = await cursor.fetchone()
    if not hist:
        raise HTTPException(status_code=404, detail="History snapshot not found")

    # Update current note with history snapshot content
    await db.execute("""
        UPDATE notes
        SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (hist["title"], hist["content"], note_id))
    await db.commit()

    c = await db.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = await c.fetchone()
    return NoteResponse(
        id=row["id"],
        folder_id=row["folder_id"],
        title=row["title"],
        content=row["content"],
        is_pinned=bool(row["is_pinned"]),
        is_deleted=bool(row["is_deleted"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"])
    )

# --- Export Endpoint ---

@router.get("/{note_id}/export/markdown")
async def export_note_markdown(note_id: str, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT title, content FROM notes WHERE id = ?", (note_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")

    filename = f"{row['title'].replace(' ', '_').lower()}.md"
    return PlainTextResponse(
        content=row["content"],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
