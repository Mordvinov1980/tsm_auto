"""
Публичные эндпоинты для водителей (БЕЗ авторизации).
Заявки с QR-наклеек: форма на /driver.
Фото НЕ хранятся на VPS — прикрепляются только к письму.
"""
import re
import json
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Request, Form, File, UploadFile
from sqlmodel import select

from backend.db import get_session
from backend.models.driver_request import DriverRequest
from backend.models.vehicle import Vehicle
from backend.models.catalog import Part
from backend.config import load_json
from backend.rate_limit import limiter

router = APIRouter()

MAX_PHOTOS = 3
MAX_PHOTO_BYTES = 5 * 1024 * 1024  # 5 МБ
ALLOWED_EXT = {"jpg", "jpeg", "png", "webp", "heic"}
OWNER_EMAIL = "oleg.mordvinov.1980@mail.ru"


@router.get("/vehicles")
async def public_vehicles():
    """Публичный список госномеров для селекта на /driver (без имён клиентов)."""
    with get_session() as session:
        rows = session.exec(select(Vehicle).where(Vehicle.is_active == True)).all()
    return {
        "status": "ok",
        "vehicles": [
            {"plate": v.plate, "brand": v.brand or "", "model": v.model or ""}
            for v in rows if v.plate
        ],
    }


@router.get("/parts")
async def public_parts():
    """Публичный список запчастей для выбора на /driver."""
    with get_session() as session:
        rows = session.exec(select(Part).where(Part.is_active == True)).all()
    return {
        "status": "ok",
        "parts": [{"name": p.name} for p in rows if p.name]
    }


@router.post("/request")
@limiter.limit("5/hour")
async def submit_request(
    request: Request,
    plate: str = Form(...),
    phone: str = Form(...),
    description: str = Form(""),
    desired_date: str = Form(""),
    parts: str = Form("{}"),  # JSON: {"название": количество}
    photos: List[UploadFile] = File(default=[]),
):
    """Приём заявки с QR. Фото уходят только в письмо, на сервере не сохраняются."""
    plate = re.sub(r"[^A-Za-zА-Яа-яЁё0-9]", "", plate).upper()[:12]
    phone = phone.strip()[:20]
    description = description.strip()[:500]
    desired_date = desired_date.strip()[:20]

    if len(plate) < 6:
        raise HTTPException(400, "Укажите госномер")
    if len(re.sub(r"\D", "", phone)) < 10:
        raise HTTPException(400, "Укажите телефон для связи")
    if len(photos) > MAX_PHOTOS:
        raise HTTPException(400, f"Максимум {MAX_PHOTOS} фото")

    # Читаем фото в память (на диск НЕ пишем)
    photo_blobs = []
    for p in photos:
        data = await p.read()
        if not data:
            continue
        if len(data) > MAX_PHOTO_BYTES:
            raise HTTPException(400, "Фото слишком большое (макс. 5 МБ)")
        ext = (p.filename or "photo.jpg").rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_EXT:
            ext = "jpg"
        photo_blobs.append((ext, data))

    # Парсим запчасти
    try:
        parts_dict = json.loads(parts) if parts else {}
        parts_str = json.dumps(parts_dict, ensure_ascii=False)
    except:
        parts_str = "{}"

    # Заявка в БД (без фото)
    with get_session() as session:
        row = DriverRequest(
            plate=plate, phone=phone,
            description=description,
            desired_date=desired_date,
            parts=parts_str,
        )
        session.add(row)
        session.commit()
        session.refresh(row)

    # Формируем текст письма с запчастями
    parts_text = ""
    if parts_dict:
        parts_lines = [f"   • {name} × {count}" for name, count in parts_dict.items() if count > 0]
        if parts_lines:
            parts_text = "🔧 Запчасти:\n" + "\n".join(parts_lines) + "\n\n"

    # Письмо владельцу с вложениями
    try:
        cfg = load_json("email.json")
        sender_email = cfg.get("sender_email", "")
        sender_password = cfg.get("sender_password", "")

        if sender_email and sender_password:
            text = (
                f"🚛 ЗАЯВКА С QR-НАКЛЕЙКИ #{row.id}\n"
                f"{'=' * 50}\n\n"
                f"🚘 Госномер: {plate}\n"
                f"🔧 Что сломалось: {description or '—'}\n"
                f"{parts_text}"
                f"📞 Телефон: {phone}\n"
                f"📅 Когда приедет: {desired_date or 'не указана'}\n"
                f"📷 Фото: {len(photo_blobs)} шт.\n\n"
                f"⏰ Время заявки: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
                f"{'=' * 50}\n"
                f"✅ TSM Auto v3.0\n"
                f"📱 Сформировано автоматически"
            )

            def make_msg(with_photos: bool) -> MIMEMultipart:
                m = MIMEMultipart()
                m["From"] = sender_email
                m["To"] = OWNER_EMAIL
                m["Subject"] = f"🚛 Заявка с QR #{row.id} — {plate}"
                m.attach(MIMEText(text, "plain", "utf-8"))
                if with_photos:
                    for i, (ext, data) in enumerate(photo_blobs, 1):
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(data)
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f'attachment; filename="photo_{i}.{ext}"',
                        )
                        m.attach(part)
                return m

            def send(msg: MIMEMultipart):
                server = smtplib.SMTP_SSL(cfg.get("smtp_server", "smtp.mail.ru"), cfg.get("smtp_port", 465))
                server.login(sender_email, sender_password)
                server.send_message(msg)
                server.quit()

            try:
                send(make_msg(with_photos=bool(photo_blobs)))
                print(f"✅ Email с {len(photo_blobs)} фото → {OWNER_EMAIL}")
            except Exception as e:
                print(f"⚠️ Письмо с фото не ушло ({e}); повтор без фото")
                send(make_msg(with_photos=False))
    except Exception as e:
        print(f"⚠️ Ошибка отправки email: {e}")

    return {"status": "ok", "id": row.id}