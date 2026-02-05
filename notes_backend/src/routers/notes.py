"""Notes CRUD API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from src.models import db as notes_db
from src.schemas.notes import NoteCreate, NoteOut, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get(
    "",
    response_model=list[NoteOut],
    summary="List notes",
    description="Return all notes, ordered by most recently updated.",
    operation_id="listNotes",
)
def list_notes() -> list[NoteOut]:
    """List all notes."""
    return notes_db.list_notes()


@router.get(
    "/{note_id}",
    response_model=NoteOut,
    summary="Get note",
    description="Return a single note by ID.",
    operation_id="getNote",
)
def get_note(note_id: int) -> NoteOut:
    """Get a note by id. Raises 404 if not found."""
    note = notes_db.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.post(
    "",
    response_model=NoteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create note",
    description="Create a new note with title and content.",
    operation_id="createNote",
)
def create_note(payload: NoteCreate) -> NoteOut:
    """Create a note."""
    return notes_db.create_note(title=payload.title, content=payload.content)


@router.put(
    "/{note_id}",
    response_model=NoteOut,
    summary="Update note",
    description="Update an existing note by ID. Fields omitted from the payload are left unchanged.",
    operation_id="updateNote",
)
def update_note(note_id: int, payload: NoteUpdate) -> NoteOut:
    """Update a note. Raises 404 if not found."""
    note = notes_db.update_note(note_id=note_id, title=payload.title, content=payload.content)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete note",
    description="Delete an existing note by ID.",
    operation_id="deleteNote",
)
def delete_note(note_id: int) -> None:
    """Delete a note. Raises 404 if not found."""
    deleted = notes_db.delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return None
