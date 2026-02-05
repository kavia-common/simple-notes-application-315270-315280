"""Pydantic schemas for notes CRUD."""

from __future__ import annotations

from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    """Shared note fields."""

    title: str = Field(..., description="Short note title", min_length=1, max_length=200)
    content: str = Field(..., description="Note content/body", min_length=1)


class NoteCreate(NoteBase):
    """Payload to create a new note."""

    pass


class NoteUpdate(BaseModel):
    """Payload to update an existing note.

    All fields are optional; omitted fields are left unchanged.
    """

    title: str | None = Field(None, description="Updated title", min_length=1, max_length=200)
    content: str | None = Field(None, description="Updated content/body", min_length=1)


class NoteOut(NoteBase):
    """Note representation returned by the API."""

    id: int = Field(..., description="Note ID")
    created_at: str = Field(..., description="UTC ISO-8601 timestamp when the note was created")
    updated_at: str = Field(..., description="UTC ISO-8601 timestamp when the note was last updated")
