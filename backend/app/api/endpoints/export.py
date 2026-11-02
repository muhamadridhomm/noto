from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import Response, HTMLResponse
import aiosqlite
from pydantic import BaseModel
from ...db.database import get_db
from ...services.export_service import generate_excel_export, generate_html_export
from .notes import list_all_tasks, list_all_targets

router = APIRouter(prefix="/export", tags=["export"])


class ExportPayload(BaseModel):
    tasks: Optional[List[dict]] = None
    targets: Optional[List[dict]] = None
    title: Optional[str] = "Combined Master Timeline & Task Hub"


@router.get("/excel")
async def export_master_excel_get(
    folder_id: Optional[str] = Query(None),
    note_id: Optional[str] = Query(None),
    db: aiosqlite.Connection = Depends(get_db)
):
    tasks = await list_all_tasks(db=db)
    targets = await list_all_targets(db=db)

    task_dicts = [t.model_dump() for t in tasks]
    target_dicts = [tgt.model_dump() for tgt in targets]

    if folder_id:
        task_dicts = [t for t in task_dicts if (t.get("folder_id") or "root") == folder_id]
        target_dicts = [tgt for tgt in target_dicts if (tgt.get("folder_id") or "root") == folder_id]

    if note_id:
        task_dicts = [t for t in task_dicts if t.get("note_id") == note_id]
        target_dicts = [tgt for tgt in target_dicts if tgt.get("note_id") == note_id]

    excel_bytes = generate_excel_export(task_dicts, target_dicts, title="Noto Master Timeline")

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="noto-master-timeline.xlsx"'
        }
    )


@router.post("/excel")
async def export_master_excel_post(
    payload: ExportPayload,
    db: aiosqlite.Connection = Depends(get_db)
):
    if payload.tasks is not None and payload.targets is not None:
        task_dicts = payload.tasks
        target_dicts = payload.targets
    else:
        tasks = await list_all_tasks(db=db)
        targets = await list_all_targets(db=db)
        task_dicts = [t.model_dump() for t in tasks]
        target_dicts = [tgt.model_dump() for tgt in targets]

    excel_bytes = generate_excel_export(task_dicts, target_dicts, title=payload.title or "Noto Master Timeline")

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="noto-master-timeline.xlsx"'
        }
    )


@router.get("/html")
async def export_master_html_get(
    folder_id: Optional[str] = Query(None),
    note_id: Optional[str] = Query(None),
    db: aiosqlite.Connection = Depends(get_db)
):
    tasks = await list_all_tasks(db=db)
    targets = await list_all_targets(db=db)

    task_dicts = [t.model_dump() for t in tasks]
    target_dicts = [tgt.model_dump() for tgt in targets]

    if folder_id:
        task_dicts = [t for t in task_dicts if (t.get("folder_id") or "root") == folder_id]
        target_dicts = [tgt for tgt in target_dicts if (tgt.get("folder_id") or "root") == folder_id]

    if note_id:
        task_dicts = [t for t in task_dicts if t.get("note_id") == note_id]
        target_dicts = [tgt for tgt in target_dicts if tgt.get("note_id") == note_id]

    html_content = generate_html_export(task_dicts, target_dicts, title="Combined Master Timeline & Roadmap Report")

    return Response(
        content=html_content,
        media_type="text/html",
        headers={
            "Content-Disposition": 'attachment; filename="noto-master-timeline.html"'
        }
    )


@router.post("/html")
async def export_master_html_post(
    payload: ExportPayload,
    db: aiosqlite.Connection = Depends(get_db)
):
    if payload.tasks is not None and payload.targets is not None:
        task_dicts = payload.tasks
        target_dicts = payload.targets
    else:
        tasks = await list_all_tasks(db=db)
        targets = await list_all_targets(db=db)
        task_dicts = [t.model_dump() for t in tasks]
        target_dicts = [tgt.model_dump() for tgt in targets]

    html_content = generate_html_export(task_dicts, target_dicts, title=payload.title or "Combined Master Timeline & Roadmap Report")

    return Response(
        content=html_content,
        media_type="text/html",
        headers={
            "Content-Disposition": 'attachment; filename="noto-master-timeline.html"'
        }
    )
