"""API routes for content management."""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile, File
from sqlmodel import func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Content,
    ContentCreate,
    ContentUpdate,
    ContentsPublic,
    ContentPublic,
    ContentStatus,
    Message,
)

router = APIRouter()


@router.get("/", response_model=ContentsPublic)
def read_contents(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    status: ContentStatus | None = None,
    campaign_id: uuid.UUID | None = None,
) -> Any:
    """
    Retrieve content items.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Content)
        count = session.exec(count_statement).one()
        statement = select(Content).offset(skip).limit(limit)
        contents = session.exec(statement).all()
    else:
        contents = crud.get_contents_by_owner(
            session=session,
            owner_id=current_user.id,
            status=status,
            campaign_id=campaign_id,
            skip=skip,
            limit=limit,
        )
        count_statement = (
            select(func.count())
            .select_from(Content)
            .where(Content.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()

    return ContentsPublic(data=contents, count=count)


@router.get("/{id}", response_model=ContentPublic)
def read_content(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get content by ID.
    """
    content = crud.get_content(session=session, content_id=id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if not current_user.is_superuser and (content.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return content


@router.post("/", response_model=ContentPublic)
def create_content(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    content_in: ContentCreate,
) -> Any:
    """
    Create new content.
    """
    content = crud.create_content(
        session=session, content_in=content_in, owner_id=current_user.id
    )
    return content


@router.put("/{id}", response_model=ContentPublic)
def update_content(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    content_in: ContentUpdate,
) -> Any:
    """
    Update content.
    """
    content = crud.get_content(session=session, content_id=id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if not current_user.is_superuser and (content.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    content = crud.update_content(session=session, db_content=content, content_in=content_in)
    return content


@router.patch("/{id}/status", response_model=ContentPublic)
def update_content_status(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    status: ContentStatus,
) -> Any:
    """
    Update content status.
    """
    content = crud.get_content(session=session, content_id=id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if not current_user.is_superuser and (content.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    content = crud.update_content_status(session=session, content_id=id, status=status)
    return content


@router.delete("/{id}")
def delete_content(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete content.
    """
    content = crud.get_content(session=session, content_id=id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if not current_user.is_superuser and (content.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(content)
    session.commit()
    return Message(message="Content deleted successfully")


@router.get("/stats/summary")
def get_content_stats(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get content statistics for current user.
    """
    stats = crud.get_content_stats_by_owner(session=session, owner_id=current_user.id)
    return stats
