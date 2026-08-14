"""
Роутер заявок на запчасти.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
import json
from datetime import date

from backend.db import get_session
from backend.models.order import Order
from backend.models.catalog import Part
from backend.config import load_json
from backend.auth import require_master

router = APIRouter()


@router.get("")
async def get_requests(
    date_param: str = Query(..., alias="date"),
    user: dict = Depends(require_master)
):
    """Формирование заявки на запчасти по дате (ДД.ММ.ГГГГ)."""
    try:
        day, month, year = date_param.split('.')
        day_i, month_i, year_i = int(day), int(month), int(year)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты")

    date_dot = date_param
    date_dash = f"{year_i}-{month_i:02d}-{day_i:02d}"

    with get_session() as session:
        parts = session.exec(select(Part).where(Part.is_active == True)).all()
        parts_map = {}
        for part in parts:
            if part.linked_work:
                for work_name in part.linked_work.split('|'):
                    key = work_name.strip()
                    if key:
                        parts_map[key] = part.name

        orders = session.exec(
            select(Order).where(
                (Order.date == date_dot) | (Order.date == date_dash)
            )
        ).all()

    result = {}
    
    for order in orders:
        from backend.models.vehicle import Vehicle
        vehicle_plate = ""
        with get_session() as s:
            v = s.exec(select(Vehicle).where(Vehicle.id == order.vehicle_id)).first()
            if v:
                vehicle_plate = v.plate
        
        for work in order.works:
            work_name = work.get("name", "").strip()
            
            if not work_name.startswith("Замена "):
                continue
            
            part_name = parts_map.get(work_name)
            if not part_name:
                continue
            
            if part_name not in result:
                result[part_name] = {"name": part_name, "count": 0, "vehicles": []}
            
            qty = work.get("quantity", 1)
            result[part_name]["count"] += qty
            if vehicle_plate and vehicle_plate not in result[part_name]["vehicles"]:
                result[part_name]["vehicles"].append(vehicle_plate)

    parts_list = sorted(result.values(), key=lambda x: x["name"])
    
    return {
        "status": "ok",
        "date": date_param,
        "orders_count": len(orders),
        "parts": parts_list,
        "total_parts": len(parts_list)
    }


@router.get("/recipients")
async def get_recipients(user: dict = Depends(require_master)):
    """Получить email-получателей заявок (admin, manager, master)."""
    recipients = load_json("email.json").get("recipients", {})
    return {"status": "ok", "recipients": recipients}


@router.post("/send-email")
async def send_request_email(request_data: dict, user: dict = Depends(require_master)):
    """Отправка заявки на email."""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    from backend.config import load_json

    email_config = load_json("email.json")

    smtp_server = email_config.get("smtp_server", "smtp.mail.ru")
    smtp_port = email_config.get("smtp_port", 465)
    sender_email = email_config.get("sender_email", "")
    sender_password = email_config.get("sender_password", "")
    recipients_config = email_config.get("recipients", {})

    date_str = request_data.get("date", "")
    parts = request_data.get("parts", [])
    recipient_types = request_data.get("recipients", [])

    if not parts:
        raise HTTPException(status_code=400, detail="Заявка пуста")

    # ⬇️ БЕРЁМ ГОТОВЫЙ ТЕКСТ С ФРОНТА, ЕСЛИ ОН ПЕРЕДАН
    text = request_data.get("text")
    if not text:
        # Fallback: старая табличная генерация (если фронт не передал text)
        text = f"📦 ЗАЯВКА НА ЗАПЧАСТИ за {date_str}\n"
        text += "=" * 60 + "\n\n"
        text += f"Всего позиций: {len(parts)}\n\n"
        text += f"{'№':<4} {'Деталь':<40} {'Кол-во':>6} {'Госномера'}\n"
        text += "-" * 60 + "\n"

        for i, part in enumerate(parts, 1):
            name = part.get('name', '')[:38]
            count = part.get('count', 0)
            vehicles = ", ".join(part.get('vehicles', []))
            text += f"{i:<4} {name:<40} {count:>6} {vehicles}\n"

        text += f"\n{'=' * 60}\n"
        text += "✅ TSM Auto v3.0\n"
        text += "📱 Сформировано автоматически"

    sent_count = 0
    for recipient_type in recipient_types:
        recipient_email = recipients_config.get(recipient_type, sender_email)
        if not recipient_email:
            continue

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"📦 Заявка на запчасти за {date_str}"
        msg.attach(MIMEText(text, 'plain', 'utf-8'))

        try:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            sent_count += 1
        except Exception as e:
            print(f"Ошибка отправки на {recipient_email}: {e}")

    return {"status": "ok", "message": f"✅ Отправлено {sent_count} получателю(ей)"}
