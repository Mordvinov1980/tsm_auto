"""
Роутер заказов.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from typing import Optional

from backend.db import get_session
from backend.models.order import Order
from backend.models.catalog import Part
from backend.auth import require_master, require_any
from backend.services.order_service import OrderService

router = APIRouter()
service = OrderService()


@router.post("")
async def create_order(
    body: dict,
    user: dict = Depends(require_master)
):
    """Создать заказ-наряд."""
    try:
        order = service.create_order(body, user["user_id"])
        return {
            "status": "ok",
            "message": f"✅ ЗН №{order.zn_number} создан",
            "order": service._order_to_dict(order)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def get_orders(
    status: Optional[str] = Query(None),
    client_id: Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    user: dict = Depends(require_any)
):
    """Список заказов."""
    filters = {}
    if status:
        filters["status"] = status
    if client_id:
        filters["client_id"] = client_id
    if date_from:
        filters["date_from"] = date_from
    if date_to:
        filters["date_to"] = date_to
    
    orders = service.get_orders(filters)
    return {"status": "ok", "orders": orders, "count": len(orders)}


@router.get("/{order_id}")
async def get_order(
    order_id: str,
    user: dict = Depends(require_any)
):
    """Детали заказа."""
    order = service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return {"status": "ok", "order": order}


# 🔧 DELETE должен быть ПЕРЕД PUT /{order_id}/status
@router.delete("/{order_id}")
async def delete_order(
    order_id: str,
    session: Session = Depends(get_session),
    user: dict = Depends(require_master)
):
    """Удалить заказ. Админ может удалить любой, остальные — только draft."""
    order = session.exec(select(Order).where(Order.order_id == order_id)).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    # Админ может удалить любой заказ
    if user["role"] != "admin" and order.status != "draft":
        raise HTTPException(status_code=403, detail="Можно удалить только черновик")
    
    # Возвращаем запчасти на склад
    for mat in order.materials:
        part = session.exec(select(Part).where(Part.name == mat["name"])).first()
        if part:
            part.quantity += mat.get("quantity", 1)
    
    session.delete(order)
    session.commit()
    return {"status": "ok", "message": "✅ Заказ удалён"}

@router.put("/{order_id}/status")
async def update_order_status(
    order_id: str,
    body: dict,
    user: dict = Depends(require_master)
):
    """Сменить статус."""
    try:
        order = service.update_status(order_id, body["status"])
        return {
            "status": "ok",
            "message": f"✅ Статус изменён на '{body['status']}'",
            "order": service._order_to_dict(order)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
