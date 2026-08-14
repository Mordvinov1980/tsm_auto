"""
Роутер справочника клиентов.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from typing import Optional

from backend.db import get_session
from backend.models.client import Client
from backend.models.vehicle import Vehicle
from backend.auth import require_any, require_master, require_admin

router = APIRouter()


@router.get("")
async def get_clients(
    search: Optional[str] = Query(None),
    session: Session = Depends(get_session),
    user: dict = Depends(require_any)  # 👈 просмотр доступен всем ролям
):
    """Список клиентов с поиском."""
    statement = select(Client).where(Client.is_active == True)
    if search:
        statement = statement.where(
            (Client.full_name.ilike(f"%{search}%")) |
            (Client.short_name.ilike(f"%{search}%")) |
            (Client.inn.ilike(f"%{search}%"))
        )
    statement = statement.order_by(Client.full_name)
    
    clients = session.exec(statement).all()
    return {
        "status": "ok",
        "clients": [
            {
                "id": c.id,
                "full_name": c.full_name,
                "short_name": c.short_name,
                "inn": c.inn,
                "phone": c.phone,
                "email": c.email
            }
            for c in clients
        ]
    }


@router.get("/{client_id}")
async def get_client(
    client_id: int,
    session: Session = Depends(get_session),
    user: dict = Depends(require_any)  # 👈 просмотр доступен всем
):
    """Детали клиента + список автомобилей."""
    client = session.exec(select(Client).where(Client.id == client_id)).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    
    vehicles = session.exec(
        select(Vehicle).where(Vehicle.client_id == client_id, Vehicle.is_active == True)
    ).all()
    
    return {
        "status": "ok",
        "client": {
            "id": client.id,
            "full_name": client.full_name,
            "short_name": client.short_name,
            "inn": client.inn,
            "kpp": client.kpp,
            "address": client.address,
            "phone": client.phone,
            "email": client.email,
            "contact_person": client.contact_person,
            "notes": client.notes,
            "vehicles": [
                {
                    "id": v.id,
                    "plate": v.plate,
                    "vin": v.vin,
                    "brand": v.brand,
                    "model": v.model,
                    "year": v.year
                }
                for v in vehicles
            ]
        }
    }


@router.post("")
async def create_client(
    body: dict,
    session: Session = Depends(get_session),
    user: dict = Depends(require_master)  # 👈 создание — мастер и выше
):
    """Создать клиента."""
    client = Client(
        full_name=body["full_name"],
        short_name=body.get("short_name", ""),
        inn=body.get("inn", ""),
        kpp=body.get("kpp", ""),
        address=body.get("address", ""),
        phone=body.get("phone", ""),
        email=body.get("email", ""),
        contact_person=body.get("contact_person", ""),
        notes=body.get("notes", "")
    )
    session.add(client)
    session.commit()
    session.refresh(client)
    return {"status": "ok", "client": {"id": client.id, "full_name": client.full_name}}
    
@router.post("/{client_id}/vehicles")
async def add_vehicle(
    client_id: int,
    body: dict,
    session: Session = Depends(get_session),
    user: dict = Depends(require_master)
):
    """Добавить автомобиль клиенту."""
    vehicle = Vehicle(
        client_id=client_id,
        plate=body.get("plate", ""),
        brand=body.get("brand", ""),
        model=body.get("model", ""),
        year=body.get("year", 0),
        vin=body.get("vin", "")
    )
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)
    return {"status": "ok", "vehicle": {"id": vehicle.id, "plate": vehicle.plate}}    
    
@router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    user: dict = Depends(require_admin)
):
    """Удалить клиента и все его автомобили (только админ)."""
    with get_session() as session:
        client = session.exec(select(Client).where(Client.id == client_id)).first()
        if not client:
            raise HTTPException(status_code=404, detail="Не найден")
        
        # Удаляем все автомобили клиента
        vehicles = session.exec(select(Vehicle).where(Vehicle.client_id == client_id)).all()
        for v in vehicles:
            session.delete(v)
        
        # Удаляем клиента
        session.delete(client)
        session.commit()
        return {"status": "ok", "message": "✅ Клиент и автомобили удалены"}

@router.delete("/{client_id}/vehicles/{vehicle_id}")
async def delete_vehicle(
    client_id: int,
    vehicle_id: int,
    user: dict = Depends(require_admin)
):
    """Удалить автомобиль (только админ)."""
    with get_session() as session:
        vehicle = session.exec(select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.client_id == client_id)).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Не найден")
        session.delete(vehicle)
        session.commit()
        return {"status": "ok"}
