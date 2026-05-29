"""
Скрипт для заполнения базы тестовыми данными.
Запуск: python -m tools.seed_data
"""
import sys
from pathlib import Path

# Добавляем корень проекта в path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.db import init_db, get_session
from backend.models.client import Client
from backend.models.vehicle import Vehicle
from backend.models.catalog import Work, Part
from backend.models.performer import Performer
from backend.models.user import User
from backend.auth import hash_password
from sqlmodel import select


def seed():
    init_db()
    session = get_session()

    # ========== ПОЛЬЗОВАТЕЛИ ==========
    users_data = [
        {"login": "admin", "password": "admin123", "full_name": "Администратор", "role": "admin"},
        {"login": "manager", "password": "manager123", "full_name": "Иванов Иван", "role": "manager"},
        {"login": "master", "password": "master123", "full_name": "Петров Пётр", "role": "master"},
        {"login": "buh", "password": "buh123", "full_name": "Сидорова Анна", "role": "accountant"},
    ]

    for u in users_data:
        existing = session.query(User).filter(User.login == u["login"]).first()
        if not existing:
            user = User(
                login=u["login"],
                password_hash=hash_password(u["password"]),
                full_name=u["full_name"],
                role=u["role"],
                is_active=True
            )
            session.add(user)
            print(f"✅ Пользователь: {u['login']} / {u['password']} ({u['role']})")
        else:
            print(f"ℹ️ Пользователь {u['login']} уже существует")

    # ========== КЛИЕНТЫ ==========
    clients_data = [
        {
            "full_name": "ЗАО «Бриджтаун Фудс»",
            "short_name": "Бриджтаун",
            "inn": "3327101234",
            "kpp": "332701001",
            "address": "600026, г. Владимир, ул. Куйбышева д. 3",
            "phone": "+7 (4922) 45-67-89",
            "email": "info@bridgetown.ru",
            "contact_person": "Николаев А.В.",
            "vehicles": [
                {"plate": "С542ТВ33", "brand": "Mercedes-Benz", "model": "Actros MP4", "year": 2020, "vin": "WDB9634031L123456"},
                {"plate": "В129УН33", "brand": "Mercedes-Benz", "model": "Actros MP4", "year": 2021, "vin": "WDB9634031L789012"},
                {"plate": "С626ТВ33", "brand": "Mercedes-Benz", "model": "Actros MP5", "year": 2022, "vin": "WDB9634031L345678"},
            ]
        },
        {
            "full_name": "ООО «ТрансЛогистик»",
            "short_name": "ТрансЛогистик",
            "inn": "3327123456",
            "kpp": "332701002",
            "address": "600000, г. Владимир, ул. Мира, д. 15",
            "phone": "+7 (4922) 33-22-11",
            "email": "info@translog.ru",
            "contact_person": "Смирнов И.П.",
            "vehicles": [
                {"plate": "А123АА77", "brand": "Scania", "model": "R450", "year": 2021, "vin": "YS2R4X20001234567"},
            ]
        },
        {
            "full_name": "ИП Кузнецов Д.В.",
            "short_name": "Кузнецов",
            "inn": "3327080152",
            "kpp": "",
            "address": "600024, г. Владимир, пр-кт Ленина, д. 43, кв. 122",
            "phone": "+7 (910) 170-80-15",
            "email": "kuznetsov@mail.ru",
            "contact_person": "Кузнецов Д.В.",
            "vehicles": [
                {"plate": "М456ОР33", "brand": "КАМАЗ", "model": "54901", "year": 2023, "vin": "XTC549010P1234567"},
                {"plate": "К789ТУ33", "brand": "ГАЗ", "model": "Газель Next", "year": 2022, "vin": "X96G678901234567"},
            ]
        },
    ]

    for cdata in clients_data:
        existing = session.query(Client).filter(Client.full_name == cdata["full_name"]).first()
        if not existing:
            client = Client(
                full_name=cdata["full_name"],
                short_name=cdata["short_name"],
                inn=cdata["inn"],
                kpp=cdata["kpp"],
                address=cdata["address"],
                phone=cdata["phone"],
                email=cdata["email"],
                contact_person=cdata["contact_person"]
            )
            session.add(client)
            session.flush()  # Чтобы получить client.id

            for vdata in cdata["vehicles"]:
                vehicle = Vehicle(
                    client_id=client.id,
                    plate=vdata["plate"],
                    brand=vdata["brand"],
                    model=vdata["model"],
                    year=vdata["year"],
                    vin=vdata["vin"]
                )
                session.add(vehicle)

            print(f"✅ Клиент: {cdata['full_name']} ({len(cdata['vehicles'])} авто)")
        else:
            print(f"ℹ️ Клиент {cdata['full_name']} уже существует")

    # ========== РАБОТЫ ==========
    works_data = [
        # Слесарные
        {"name": "Замена масла в двигателе", "category": "mechanical", "norm_hours": 0.75, "rate_rub": 3000},
        {"name": "Замена масляного фильтра", "category": "mechanical", "norm_hours": 0.25, "rate_rub": 3000},
        {"name": "Замена воздушного фильтра", "category": "mechanical", "norm_hours": 0.3, "rate_rub": 3000},
        {"name": "Замена топливного фильтра", "category": "mechanical", "norm_hours": 0.5, "rate_rub": 3000},
        {"name": "Замена тормозных колодок (перед)", "category": "mechanical", "norm_hours": 1.0, "rate_rub": 3500},
        {"name": "Замена тормозных колодок (зад)", "category": "mechanical", "norm_hours": 1.2, "rate_rub": 3500},
        {"name": "Замена тормозных дисков (перед)", "category": "mechanical", "norm_hours": 1.5, "rate_rub": 3500},
        {"name": "Замена нижней накладки правой фары", "category": "mechanical", "norm_hours": 0.5, "rate_rub": 3000},
        {"name": "Замена нижней накладки левой фары", "category": "mechanical", "norm_hours": 0.5, "rate_rub": 3000},

        # Ремонтные
        {"name": "Диагностика двигателя", "category": "repair", "norm_hours": 1.0, "rate_rub": 4000},
        {"name": "Ремонт турбины", "category": "repair", "norm_hours": 4.0, "rate_rub": 4500},
        {"name": "Ремонт КПП", "category": "repair", "norm_hours": 6.0, "rate_rub": 5000},
        {"name": "Замена сцепления", "category": "repair", "norm_hours": 3.5, "rate_rub": 4000},

        # Покрасочные
        {"name": "Покраска кабины (полная)", "category": "painting", "norm_hours": 20.0, "rate_rub": 5000},
        {"name": "Покраска двери", "category": "painting", "norm_hours": 3.0, "rate_rub": 5000},
        {"name": "Покраска бампера", "category": "painting", "norm_hours": 2.5, "rate_rub": 5000},

        # Осмотр
        {"name": "Осмотр ходовой части", "category": "mechanical", "norm_hours": 0.5, "rate_rub": 2500},
        {"name": "Осмотр тормозной системы", "category": "mechanical", "norm_hours": 0.5, "rate_rub": 2500},
        {"name": "Осмотр электрики", "category": "repair", "norm_hours": 0.75, "rate_rub": 3000},

        # С/у
        {"name": "С/у колеса", "category": "mechanical", "norm_hours": 0.25, "rate_rub": 2500},
        {"name": "С/у аккумулятора", "category": "mechanical", "norm_hours": 0.25, "rate_rub": 2500},
    ]

    for wdata in works_data:
        existing = session.query(Work).filter(Work.name == wdata["name"]).first()
        if not existing:
            work = Work(**wdata)
            session.add(work)
    print(f"✅ Работы: {len(works_data)} позиций")

    # ========== ЗАПЧАСТИ ==========
    parts_data = [
        {"name": "Нижняя накладка правой фары", "article": "A1234567890", "unit": "шт.", "quantity": 5, "min_stock": 2, "purchase_price": 3500, "retail_price": 5000, "linked_work": "Замена нижней накладки правой фары"},
        {"name": "Нижняя накладка левой фары", "article": "A1234567891", "unit": "шт.", "quantity": 3, "min_stock": 2, "purchase_price": 3500, "retail_price": 5000, "linked_work": "Замена нижней накладки левой фары"},
        {"name": "Масло моторное 10W-40 (канистра 20л)", "article": "M-10W40-20", "unit": "канистра", "quantity": 10, "min_stock": 3, "purchase_price": 4500, "retail_price": 6500, "linked_work": "Замена масла в двигателе"},
        {"name": "Фильтр масляный", "article": "F-MB-001", "unit": "шт.", "quantity": 20, "min_stock": 5, "purchase_price": 800, "retail_price": 1500, "linked_work": "Замена масляного фильтра"},
        {"name": "Фильтр воздушный", "article": "F-MB-002", "unit": "шт.", "quantity": 15, "min_stock": 5, "purchase_price": 1200, "retail_price": 2200, "linked_work": "Замена воздушного фильтра"},
        {"name": "Фильтр топливный", "article": "F-MB-003", "unit": "шт.", "quantity": 10, "min_stock": 3, "purchase_price": 1500, "retail_price": 2800, "linked_work": "Замена топливного фильтра"},
        {"name": "Колодки тормозные передние (комплект)", "article": "B-MB-001", "unit": "комплект", "quantity": 6, "min_stock": 2, "purchase_price": 3200, "retail_price": 5500, "linked_work": "Замена тормозных колодок (перед)"},
        {"name": "Колодки тормозные задние (комплект)", "article": "B-MB-002", "unit": "комплект", "quantity": 4, "min_stock": 2, "purchase_price": 2800, "retail_price": 5000, "linked_work": "Замена тормозных колодок (зад)"},
        {"name": "Диск тормозной передний", "article": "D-MB-001", "unit": "шт.", "quantity": 4, "min_stock": 2, "purchase_price": 4500, "retail_price": 7500, "linked_work": "Замена тормозных дисков (перед)"},
        {"name": "Комплект сцепления", "article": "C-MB-001", "unit": "комплект", "quantity": 2, "min_stock": 1, "purchase_price": 15000, "retail_price": 22000, "linked_work": "Замена сцепления"},
    ]

    for pdata in parts_data:
        existing = session.query(Part).filter(Part.name == pdata["name"]).first()
        if not existing:
            part = Part(**pdata)
            session.add(part)
    print(f"✅ Запчасти: {len(parts_data)} позиций")
    
    # ========== ИСПОЛНИТЕЛИ ==========
    performers_data = [
        {"full_name": "Мордвинов", "group": "mechanical"},
        {"full_name": "Змазов", "group": "mechanical"},
        {"full_name": "Зайцев", "group": "mechanical"},
        {"full_name": "Любарский", "group": "mechanical"},
        {"full_name": "Касаткин", "group": "mechanical"},
        {"full_name": "Мордвинов", "group": "repair"},
        {"full_name": "Змазов", "group": "repair"},
        {"full_name": "Зайцев", "group": "repair"},
        {"full_name": "Любарский", "group": "repair"},
        {"full_name": "Касаткин", "group": "repair"},
        {"full_name": "Мордвинов", "group": "painting"},
        {"full_name": "Любарский", "group": "painting"},
        {"full_name": "Касаткин", "group": "painting"},
    ]

    for pdata in performers_data:
        existing = session.exec(
            select(Performer).where(
                Performer.full_name == pdata["full_name"],
                Performer.group == pdata["group"]  # ← добавить
            )
        ).first()
        if not existing:
            session.add(Performer(**pdata))
    print(f"✅ Исполнители: {len(performers_data)} чел.")    
    
    

    # ========== ФИНАЛ ==========
    session.commit()
    session.close()
    print("\n🎉 База заполнена тестовыми данными!")


if __name__ == "__main__":
    seed()
