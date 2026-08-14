"""
Роутер каталогов: работы и запчасти.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from typing import Optional

from backend.db import get_session
from backend.models.catalog import Work, Part
from backend.auth import require_any, require_manager  # 👈 require_any для просмотра

router = APIRouter()


# ========== РАБОТЫ ==========

@router.get("/works")
async def get_works(
    category: Optional[str] = Query(None),
    session: Session = Depends(get_session),
    user: dict = Depends(require_any)  # 👈 просмотр всем
):
    """Список работ (фильтр по категории)."""
    statement = select(Work).where(Work.is_active == True)
    if category:
        statement = statement.where(Work.category == category)
    statement = statement.order_by(Work.id)
    
    works = session.exec(statement).all()
    return {
        "status": "ok",
        "works": [
            {
                "id": w.id,
                "name": w.name,
                "category": w.category,
                "norm_hours": w.norm_hours,
                "rate_rub": w.rate_rub
            }
            for w in works
        ]
    }


@router.post("/works")
async def create_work(
    body: dict,
    session: Session = Depends(get_session),
    user: dict = Depends(require_manager)  # 👈 создание — manager и выше
):
    """Добавить работу (только admin/manager)."""
    work = Work(
        name=body["name"],
        category=body.get("category", "mechanical"),
        norm_hours=body.get("norm_hours", 0),
        rate_rub=body.get("rate_rub", 0)
    )
    session.add(work)
    session.commit()
    session.refresh(work)
    return {"status": "ok", "work": {"id": work.id, "name": work.name}}


# ========== ЗАПЧАСТИ ==========

@router.get("/parts")
async def get_parts(
    search: Optional[str] = Query(None),
    session: Session = Depends(get_session),
    user: dict = Depends(require_any)  # 👈 просмотр всем
):
    """Список запчастей (поиск по названию)."""
    statement = select(Part).where(Part.is_active == True)
    if search:
        statement = statement.where(Part.name.ilike(f"%{search}%"))
    statement = statement.order_by(Part.id)
    
    parts = session.exec(statement).all()
    return {
        "status": "ok",
        "parts": [
            {
                "id": p.id,
                "name": p.name,
                "article": p.article,
                "unit": p.unit,
                "quantity": p.quantity,
                "retail_price": p.retail_price,
                "linked_work": p.linked_work
            }
            for p in parts
        ]
    }


@router.post("/parts")
async def create_part(
    body: dict,
    session: Session = Depends(get_session),
    user: dict = Depends(require_manager)  # 👈 создание — manager и выше
):
    """Добавить запчасть (только admin/manager)."""
    part = Part(
        name=body["name"],
        article=body.get("article", ""),
        unit=body.get("unit", "шт."),
        quantity=body.get("quantity", 0),
        min_stock=body.get("min_stock", 0),
        purchase_price=body.get("purchase_price", 0),
        retail_price=body.get("retail_price", 0),
        linked_work=body.get("linked_work", "")
    )
    session.add(part)
    session.commit()
    session.refresh(part)
    return {"status": "ok", "part": {"id": part.id, "name": part.name}}
    
@router.delete("/works/{work_id}")
async def delete_work(
    work_id: int,
    session: Session = Depends(get_session),
    user: dict = Depends(require_manager)
):
    work = session.exec(select(Work).where(Work.id == work_id)).first()
    if not work:
        raise HTTPException(status_code=404, detail="Не найдена")
    work.is_active = False
    session.commit()
    return {"status": "ok"}

@router.delete("/parts/{part_id}")
async def delete_part(
    part_id: int,
    session: Session = Depends(get_session),
    user: dict = Depends(require_manager)
):
    part = session.exec(select(Part).where(Part.id == part_id)).first()
    if not part:
        raise HTTPException(status_code=404, detail="Не найдена")
    part.is_active = False
    session.commit()
    return {"status": "ok"}    
