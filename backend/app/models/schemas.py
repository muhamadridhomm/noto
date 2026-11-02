from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

# --- Folder Schemas ---
class FolderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon: Optional[str] = "folder"
    sort_order: Optional[int] = 0

class FolderCreate(FolderBase):
    pass

class FolderUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None

class FolderResponse(FolderBase):
    id: str
    created_at: str
    updated_at: str
    note_count: Optional[int] = 0

# --- Note Schemas ---
class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: Optional[str] = ""
    folder_id: Optional[str] = None
    is_pinned: Optional[bool] = False
    is_deleted: Optional[bool] = False

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    folder_id: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_deleted: Optional[bool] = None

class NoteResponse(NoteBase):
    id: str
    created_at: str
    updated_at: str

class NoteHistoryResponse(BaseModel):
    id: str
    note_id: str
    title: str
    content: str
    created_at: str

class GlobalTaskItem(BaseModel):
    id: str
    note_id: str
    note_title: str
    folder_id: Optional[str] = None
    folder_name: Optional[str] = None
    title: str
    done: bool
    status: str
    priority: str
    due_date: str
    group: Optional[str] = ""
    sprint: Optional[str] = ""
    notes: Optional[str] = ""

class GlobalSprintItem(BaseModel):
    id: str
    note_id: str
    note_title: str
    name: str
    goal: Optional[str] = ""
    start_date: Optional[str] = ""
    due_date: Optional[str] = ""
    status: Optional[str] = "Active"

class SprintCreate(BaseModel):
    name: str = Field(..., min_length=1)
    goal: Optional[str] = ""
    start_date: Optional[str] = ""
    due_date: Optional[str] = ""
    status: Optional[str] = "Active"

class SprintUpdate(BaseModel):
    name: Optional[str] = None
    goal: Optional[str] = None
    start_date: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None

class GlobalTargetItem(BaseModel):
    id: str
    note_id: str
    note_title: str
    folder_id: Optional[str] = None
    folder_name: Optional[str] = None
    title: str
    badge: Optional[str] = ""
    date: Optional[str] = ""
    description: Optional[str] = ""

class TargetCreate(BaseModel):
    title: str = Field(..., min_length=1)
    badge: Optional[str] = "Milestone"
    date: Optional[str] = ""
    description: Optional[str] = ""

class TargetUpdate(BaseModel):
    title: Optional[str] = None
    badge: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    group: Optional[str] = None
    sprint: Optional[str] = None
    notes: Optional[str] = None

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)
    status: Optional[str] = "To Do"
    priority: Optional[str] = "Normal"
    due_date: Optional[str] = ""
    group: Optional[str] = ""
    sprint: Optional[str] = ""
    notes: Optional[str] = ""

# --- Search Schema ---
class SearchResult(BaseModel):
    id: str
    title: str
    snippet: str
    folder_id: Optional[str] = None
    folder_name: Optional[str] = None
    updated_at: str

# --- AI Schemas ---
class AIDraftRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    context_content: Optional[str] = ""  # Selected or existing note text if tidying
    mode: str = "new_note"  # "new_note" | "tidy_note" | "custom"
    provider: Optional[str] = None  # "gemini" or "ollama" (defaults to backend setting)
    tone: Optional[str] = "balanced"  # "concise", "professional", "balanced", "bulleted"

class AISettingsResponse(BaseModel):
    default_provider: str
    gemini_configured: bool
    gemini_model: str
    ollama_url: str
    ollama_model: str
    ollama_available: bool
