"""
Роутер документов.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse

from backend.auth import require_any
from backend.services.document_service import DocumentService
from backend.config import DATA_DIR

router = APIRouter()
doc_service = DocumentService()


@router.post("/order/{order_id}")
async def generate_order_excel(
    order_id: str,
    user: dict = Depends(require_any)
):
    """Сгенерировать Excel заказ-наряда."""
    try:
        filename = doc_service.generate_order_excel(order_id)
        return {
            "status": "ok",
            "filename": filename,
            "message": "✅ Заказ-наряд сгенерирован"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
async def download_document(
    filename: str,
    user: dict = Depends(require_any)  # ← ДОБАВЬ ЭТУ СТРОКУ
):
    """Скачать сгенерированный документ."""
    filepath = DATA_DIR / "documents" / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Файл не найден")

    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename
    )
