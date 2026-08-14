"""
Роутер исполнителей.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from backend.db import get_session
from backend.models.performer import Performer
from backend.auth import require_any, require_manager

router = APIRouter()


@router.get("")
async def get_performers(
    session: Session = Depends(get_session),
    user: dict = Depends(require_any)
):
    """Список исполнителей."""
    performers = session.exec(
        select(Performer).where(Performer.is_active == True).order_by(Performer.group, Performer.full_name)
    ).all()

    # Группируем
    groups = {"mechanical": [], "repair": [], "painting": []}
    for p in performers:
        if p.group in groups:
            groups[p.group].append({"id": p.id, "full_name": p.full_name})

    return {"status": "ok", "groups": groups, "list": [
        {"id": p.id, "full_name": p.full_name, "group": p.group} for p in performers
    ]}


@router.post("")
async def create_performer(
    body: dict,
    session: Session = Depends(get_session),
    user: dict = Depends(require_manager)
):
    """Добавить исполнителя."""
    performer = Performer(
        full_name=body["full_name"],
        group=body.get("group", "mechanical")
    )
    session.add(performer)
    session.commit()
    session.refresh(performer)
    return {"status": "ok", "performer": {"id": performer.id, "full_name": performer.full_name, "group": performer.group}}


@router.delete("/{performer_id}")
async def delete_performer(
    performer_id: int,
    session: Session = Depends(get_session),
    user: dict = Depends(require_manager)
):
    """Деактивировать исполнителя."""
    performer = session.exec(select(Performer).where(Performer.id == performer_id)).first()
    if not performer:
        raise HTTPException(status_code=404, detail="Не найден")
    performer.is_active = False
    session.commit()
    return {"status": "ok", "message": "✅ Деактивирован"}
