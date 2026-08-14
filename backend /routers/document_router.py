"""
Роутер документов.
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlmodel import select

from backend.auth import require_any, get_current_user
from backend.services.document_service import DocumentService
from backend.config import DATA_DIR
from backend.db import get_session
from backend.models.order import Order
from backend.models.client import Client
from backend.models.vehicle import Vehicle
# from backend.engines.full_document_xlsx import FullDocumentGenerator

router = APIRouter()
doc_service = DocumentService()


#@router.post("/full/{order_id}")
#async def generate_full_document(order_id: str, user: dict = Depends(require_any)):
#  """Генерация полного пакета документов (Счёт + Акт + УПД)"""
#    with get_session() as session:
#        order = session.exec(select(Order).where(Order.order_id == order_id)).first()
#        if not order:
#            raise HTTPException(status_code=404, detail="Заказ не найден")
#        
#        client = session.exec(select(Client).where(Client.id == order.client_id)).first()
#        vehicle = session.exec(select(Vehicle).where(Vehicle.id == order.vehicle_id)).first()
#        
#        order_dict = {
#            "zn_number": order.zn_number,
#            "date": order.date,  # уже в формате ДД.ММ.ГГГГ — ОК
#            "client_name": client.full_name if client else "—",  # полное имя вместо short_name
#            "client_inn": client.inn if client else "",
#            "client_address": client.address if client else "",
#            "vehicle_plate": vehicle.plate if vehicle else "—",
#            "vehicle_brand": vehicle.brand if vehicle else "",       # ← добавить
#            "vehicle_model": vehicle.model if vehicle else "",       # ← добавить
#            "work_items": order.works,
#            "material_items": order.materials,
#            "total_amount": order.total_amount,
#        }    
#    gen = FullDocumentGenerator()
#    filepath = gen.generate(order_dict)
#    filename = Path(filepath).name
#    
#    return {"status": "ok", "filename": filename}


@router.post("/order/{order_id}")
async def generate_order_excel(order_id: str, user: dict = Depends(require_any)):
    """Сгенерировать Excel заказ-наряда."""
    try:
        filename = doc_service.generate_order_excel(order_id)
        return {"status": "ok", "filename": filename, "message": "✅ Заказ-наряд сгенерирован"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
async def download_document(filename: str, user: dict = Depends(require_any)):
    """Скачать сгенерированный документ."""
    filepath = DATA_DIR / "documents" / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(filepath, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=filename)
