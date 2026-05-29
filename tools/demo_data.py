#!/usr/bin/env python3
"""
Скрипт заполнения базы данных TSM Auto демо-данными.

Демо-профиль: Автосервис "ТСМ Авто"
- 8 клиентов (5 юрлиц + 3 физлица)
- 15 автомобилей
- 25 видов работ (по 3 категориям)
- 40 позиций запчастей
- 6 исполнителей (по 2 в каждой группе)
- 50 заказов за последние 3 месяца
- Разные статусы заказов (draft, in_progress, completed)

Использование:
    python tools/demo_data.py

ВНИМАНИЕ: Скрипт удаляет все существующие данные (кроме admin)!
"""

import sys
import os
import json  # ← добавь эту строку
from datetime import datetime, timedelta
from pathlib import Path
import random

# Добавляем корень проекта в sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from backend.db import engine, get_session
from backend.models.user import User
from backend.models.client import Client
from backend.models.vehicle import Vehicle
from backend.models.catalog import Work, Part
from backend.models.performer import Performer
from backend.models.order import Order
from backend.models.document import Document
from backend.auth import hash_password


def clear_database():
    """Очистка всех таблиц кроме admin пользователя."""
    print("🗑️  Очистка базы данных...")
    with get_session() as session:
        # Сохраняем admin
        admin = session.exec(select(User).where(User.login == "admin")).first()

        # Удаляем все данные
        session.exec(Document.__table__.delete())
        session.exec(Order.__table__.delete())
        session.exec(Vehicle.__table__.delete())
        session.exec(Client.__table__.delete())
        session.exec(Work.__table__.delete())
        session.exec(Part.__table__.delete())
        session.exec(Performer.__table__.delete())
        session.exec(User.__table__.delete())

        # Восстанавливаем admin
        if admin:
            session.add(admin)

        session.commit()
    print("✅ База очищена (admin сохранён)")


def create_demo_users():
    """Создание демо-пользователей."""
    print("👥 Создание пользователей...")
    users = [
        {"login": "manager", "password": "manager123", "full_name": "Смирнов Алексей Петрович", "role": "manager"},
        {"login": "master1", "password": "master123", "full_name": "Иванов Иван Иванович", "role": "master"},
        {"login": "master2", "password": "master123", "full_name": "Петров Пётр Петрович", "role": "master"},
        {"login": "buh", "password": "buh123", "full_name": "Сидорова Мария Сергеевна", "role": "accountant"},
    ]

    with get_session() as session:
        for user_data in users:
            user = User(
                login=user_data["login"],
                password_hash=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=True
            )
            session.add(user)
        session.commit()
    print(f"✅ Создано {len(users)} пользователей")


def create_demo_clients():
    """Создание демо-клиентов."""
    print("👥 Создание клиентов...")
    clients_data = [
        # Юрлица
        {
            "full_name": 'ООО "ТрансЛогистик"',
            "short_name": "ТрансЛогистик",
            "inn": "7701234567",
            "kpp": "770101001",
            "address": "г. Москва, ул. Складочная, д. 15",
            "phone": "+7 (495) 123-45-67",
            "email": "info@translogistic.ru",
            "contact_person": "Николаев Дмитрий",
        },
        {
            "full_name": 'ООО "АвтоПеревозки"',
            "short_name": "АвтоПеревозки",
            "inn": "7702345678",
            "kpp": "770201001",
            "address": "г. Москва, Каширское ш., д. 65",
            "phone": "+7 (495) 234-56-78",
            "email": "zakaz@autoperevozki.ru",
            "contact_person": "Кузнецов Андрей",
        },
        {
            "full_name": 'ИП Сорокин В.М.',
            "short_name": "ИП Сорокин",
            "inn": "770123456789",
            "kpp": "",
            "address": "г. Москва, ул. Промышленная, д. 8",
            "phone": "+7 (926) 345-67-89",
            "email": "sorokin@mail.ru",
            "contact_person": "Сорокин Виктор",
        },
        {
            "full_name": 'ООО "СтройТранс"',
            "short_name": "СтройТранс",
            "inn": "7703456789",
            "kpp": "770301001",
            "address": "г. Москва, ул. Строителей, д. 22",
            "phone": "+7 (495) 456-78-90",
            "email": "office@stroytrans.ru",
            "contact_person": "Фёдоров Игорь",
        },
        {
            "full_name": 'ООО "ГрузАвтоСервис"',
            "short_name": "ГрузАвтоСервис",
            "inn": "7704567890",
            "kpp": "770401001",
            "address": "г. Москва, Варшавское ш., д. 170",
            "phone": "+7 (495) 567-89-01",
            "email": "service@gruzavto.ru",
            "contact_person": "Морозов Сергей",
        },
        # Физлица
        {
            "full_name": "Козлов Александр Николаевич",
            "short_name": "Козлов А.Н.",
            "inn": "",
            "kpp": "",
            "address": "г. Москва, ул. Ленина, д. 45, кв. 12",
            "phone": "+7 (916) 678-90-12",
            "email": "kozlov@gmail.com",
            "contact_person": "",
        },
        {
            "full_name": "Новикова Елена Владимировна",
            "short_name": "Новикова Е.В.",
            "inn": "",
            "kpp": "",
            "address": "г. Москва, ул. Пушкина, д. 10, кв. 5",
            "phone": "+7 (903) 789-01-23",
            "email": "novikova@yandex.ru",
            "contact_person": "",
        },
        {
            "full_name": "Волков Дмитрий Сергеевич",
            "short_name": "Волков Д.С.",
            "inn": "",
            "kpp": "",
            "address": "г. Москва, ул. Гагарина, д. 30, кв. 88",
            "phone": "+7 (925) 890-12-34",
            "email": "volkov@mail.ru",
            "contact_person": "",
        },
    ]

    with get_session() as session:
        for client_data in clients_data:
            client = Client(**client_data, is_active=True)
            session.add(client)
        session.commit()
    print(f"✅ Создано {len(clients_data)} клиентов")


def create_demo_vehicles():
    """Создание демо-автомобилей."""
    print("🚛 Создание автомобилей...")

    with get_session() as session:
        clients = session.exec(select(Client)).all()

        vehicles_data = [
            # ТрансЛогистик (3 авто)
            {"client": "ТрансЛогистик", "plate": "А123АА77", "vin": "XWB12345678901234", "brand": "Mercedes-Benz", "model": "Actros", "year": 2019},
            {"client": "ТрансЛогистик", "plate": "В456ВВ77", "vin": "XWB23456789012345", "brand": "Volvo", "model": "FH16", "year": 2020},
            {"client": "ТрансЛогистик", "plate": "Е789ЕЕ77", "vin": "XWB34567890123456", "brand": "Scania", "model": "R500", "year": 2018},

            # АвтоПеревозки (2 авто)
            {"client": "АвтоПеревозки", "plate": "К012КК77", "vin": "YV345678901234567", "brand": "MAN", "model": "TGX", "year": 2021},
            {"client": "АвтоПеревозки", "plate": "М345ММ77", "vin": "YV456789012345678", "brand": "DAF", "model": "XF", "year": 2019},

            # ИП Сорокин (2 авто)
            {"client": "ИП Сорокин", "plate": "Н678НН77", "vin": "Z9456789012345678", "brand": "ГАЗ", "model": "Газель Next", "year": 2020},
            {"client": "ИП Сорокин", "plate": "Р901РР77", "vin": "Z9567890123456789", "brand": "ГАЗ", "model": "Газон Next", "year": 2021},

            # СтройТранс (3 авто)
            {"client": "СтройТранс", "plate": "С234СС77", "vin": "WDB67890123456789", "brand": "Mercedes-Benz", "model": "Atego", "year": 2018},
            {"client": "СтройТранс", "plate": "Т567ТТ77", "vin": "WDB78901234567890", "brand": "Iveco", "model": "Stralis", "year": 2017},
            {"client": "СтройТранс", "plate": "У890УУ77", "vin": "WDB89012345678901", "brand": "Renault", "model": "Premium", "year": 2019},

            # ГрузАвтоСервис (2 авто)
            {"client": "ГрузАвтоСервис", "plate": "Х123ХХ77", "vin": "VF190123456789012", "brand": "Renault", "model": "Kerax", "year": 2020},
            {"client": "ГрузАвтоСервис", "plate": "Ц456ЦЦ77", "vin": "VF201234567890123", "brand": "Volvo", "model": "FMX", "year": 2021},

            # Физлица (по 1 авто)
            {"client": "Козлов А.Н.", "plate": "Ч789ЧЧ77", "vin": "WVW12345678901234", "brand": "Volkswagen", "model": "Transporter", "year": 2016},
            {"client": "Новикова Е.В.", "plate": "Ш012ШШ77", "vin": "WVW23456789012345", "brand": "Ford", "model": "Transit", "year": 2018},
            {"client": "Волков Д.С.", "plate": "Э345ЭЭ77", "vin": "WVW34567890123456", "brand": "Peugeot", "model": "Boxer", "year": 2017},
        ]

        for vehicle_data in vehicles_data:
            client = session.exec(select(Client).where(Client.short_name == vehicle_data["client"])).first()
            if client:
                vehicle = Vehicle(
                    client_id=client.id,
                    plate=vehicle_data["plate"],
                    vin=vehicle_data["vin"],
                    brand=vehicle_data["brand"],
                    model=vehicle_data["model"],
                    year=vehicle_data["year"],
                    is_active=True
                )
                session.add(vehicle)

        session.commit()
    print(f"✅ Создано {len(vehicles_data)} автомобилей")


def create_demo_works():
    """Создание демо-каталога работ."""
    print("🔧 Создание каталога работ...")

    works_data = [
        # Mechanical (слесарные работы)
        {"name": "Осмотр ТС", "category": "mechanical", "norm_hours": 0.5, "rate_rub": 800},
        {"name": "Замена масла двигателя", "category": "mechanical", "norm_hours": 1.0, "rate_rub": 1000},
        {"name": "Замена масляного фильтра", "category": "mechanical", "norm_hours": 0.3, "rate_rub": 800},
        {"name": "Замена тормозных колодок передних", "category": "mechanical", "norm_hours": 1.5, "rate_rub": 1200},
        {"name": "Замена тормозных колодок задних", "category": "mechanical", "norm_hours": 1.5, "rate_rub": 1200},
        {"name": "Замена тормозных дисков", "category": "mechanical", "norm_hours": 2.0, "rate_rub": 1500},
        {"name": "Диагностика тормозной системы", "category": "mechanical", "norm_hours": 1.0, "rate_rub": 900},
        {"name": "Замена ремня ГРМ", "category": "mechanical", "norm_hours": 4.0, "rate_rub": 1800},
        {"name": "Замена помпы", "category": "mechanical", "norm_hours": 3.0, "rate_rub": 1600},
        {"name": "Замена радиатора", "category": "mechanical", "norm_hours": 2.5, "rate_rub": 1500},

        # Repair (ремонтные работы)
        {"name": "Ремонт двигателя (капитальный)", "category": "repair", "norm_hours": 40.0, "rate_rub": 2000},
        {"name": "Замена прокладки ГБЦ", "category": "repair", "norm_hours": 8.0, "rate_rub": 1800},
        {"name": "Ремонт КПП", "category": "repair", "norm_hours": 16.0, "rate_rub": 1900},
        {"name": "Замена сцепления", "category": "repair", "norm_hours": 6.0, "rate_rub": 1700},
        {"name": "Ремонт подвески", "category": "repair", "norm_hours": 5.0, "rate_rub": 1600},
        {"name": "Замена амортизаторов", "category": "repair", "norm_hours": 2.0, "rate_rub": 1400},
        {"name": "Замена сайлентблоков", "category": "repair", "norm_hours": 3.0, "rate_rub": 1500},
        {"name": "Ремонт рулевого управления", "category": "repair", "norm_hours": 4.0, "rate_rub": 1600},

        # Painting (покрасочные работы)
        {"name": "Покраска бампера", "category": "painting", "norm_hours": 6.0, "rate_rub": 2500},
        {"name": "Покраска крыла", "category": "painting", "norm_hours": 8.0, "rate_rub": 2800},
        {"name": "Покраска двери", "category": "painting", "norm_hours": 10.0, "rate_rub": 3000},
        {"name": "Покраска капота", "category": "painting", "norm_hours": 12.0, "rate_rub": 3200},
        {"name": "Полировка кузова", "category": "painting", "norm_hours": 4.0, "rate_rub": 2000},
        {"name": "Антикоррозийная обработка", "category": "painting", "norm_hours": 8.0, "rate_rub": 2200},
        {"name": "Локальный ремонт ЛКП", "category": "painting", "norm_hours": 3.0, "rate_rub": 2400},
    ]

    with get_session() as session:
        for work_data in works_data:
            work = Work(**work_data, is_active=True)
            session.add(work)
        session.commit()
    print(f"✅ Создано {len(works_data)} видов работ")


def create_demo_parts():
    """Создание демо-каталога запчастей."""
    print("📦 Создание каталога запчастей...")

    parts_data = [
        # Фильтры
        {"name": "Фильтр масляный", "article": "MF-001", "unit": "шт", "quantity": 50, "min_stock": 10, "purchase_price": 300, "retail_price": 500, "linked_work": "Замена масляного фильтра"},
        {"name": "Фильтр воздушный", "article": "AF-001", "unit": "шт", "quantity": 30, "min_stock": 5, "purchase_price": 400, "retail_price": 650, "linked_work": ""},
        {"name": "Фильтр топливный", "article": "FF-001", "unit": "шт", "quantity": 25, "min_stock": 5, "purchase_price": 500, "retail_price": 800, "linked_work": ""},
        {"name": "Фильтр салонный", "article": "CF-001", "unit": "шт", "quantity": 20, "min_stock": 5, "purchase_price": 350, "retail_price": 550, "linked_work": ""},

        # Масла и жидкости
        {"name": "Масло моторное 5W-40 (5л)", "article": "OL-001", "unit": "шт", "quantity": 40, "min_stock": 10, "purchase_price": 2500, "retail_price": 3500, "linked_work": "Замена масла двигателя"},
        {"name": "Масло трансмиссионное 75W-90 (1л)", "article": "OL-002", "unit": "шт", "quantity": 30, "min_stock": 5, "purchase_price": 800, "retail_price": 1200, "linked_work": ""},
        {"name": "Антифриз G12 (5л)", "article": "CL-001", "unit": "шт", "quantity": 20, "min_stock": 5, "purchase_price": 1200, "retail_price": 1800, "linked_work": ""},
        {"name": "Тормозная жидкость DOT-4 (1л)", "article": "BF-001", "unit": "шт", "quantity": 25, "min_stock": 5, "purchase_price": 600, "retail_price": 900, "linked_work": ""},

        # Тормозная система
        {"name": "Колодки тормозные передние", "article": "BP-001", "unit": "компл", "quantity": 20, "min_stock": 5, "purchase_price": 2500, "retail_price": 3500, "linked_work": "Замена тормозных колодок передних"},
        {"name": "Колодки тормозные задние", "article": "BP-002", "unit": "компл", "quantity": 20, "min_stock": 5, "purchase_price": 2200, "retail_price": 3200, "linked_work": "Замена тормозных колодок задних"},
        {"name": "Диск тормозной передний", "article": "BD-001", "unit": "шт", "quantity": 15, "min_stock": 3, "purchase_price": 3500, "retail_price": 5000, "linked_work": "Замена тормозных дисков"},
        {"name": "Диск тормозной задний", "article": "BD-002", "unit": "шт", "quantity": 15, "min_stock": 3, "purchase_price": 3000, "retail_price": 4500, "linked_work": "Замена тормозных дисков"},

        # Двигатель
        {"name": "Ремень ГРМ", "article": "TB-001", "unit": "шт", "quantity": 10, "min_stock": 2, "purchase_price": 4000, "retail_price": 6000, "linked_work": "Замена ремня ГРМ"},
        {"name": "Помпа водяная", "article": "WP-001", "unit": "шт", "quantity": 8, "min_stock": 2, "purchase_price": 5000, "retail_price": 7500, "linked_work": "Замена помпы"},
        {"name": "Радиатор охлаждения", "article": "RD-001", "unit": "шт", "quantity": 5, "min_stock": 1, "purchase_price": 12000, "retail_price": 18000, "linked_work": "Замена радиатора"},
        {"name": "Прокладка ГБЦ", "article": "HG-001", "unit": "шт", "quantity": 6, "min_stock": 2, "purchase_price": 3000, "retail_price": 4500, "linked_work": "Замена прокладки ГБЦ"},
        {"name": "Свеча зажигания", "article": "SP-001", "unit": "шт", "quantity": 100, "min_stock": 20, "purchase_price": 300, "retail_price": 500, "linked_work": ""},

        # Трансмиссия
        {"name": "Диск сцепления", "article": "CD-001", "unit": "шт", "quantity": 8, "min_stock": 2, "purchase_price": 6000, "retail_price": 9000, "linked_work": "Замена сцепления"},
        {"name": "Корзина сцепления", "article": "CP-001", "unit": "шт", "quantity": 8, "min_stock": 2, "purchase_price": 7000, "retail_price": 10500, "linked_work": "Замена сцепления"},
        {"name": "Выжимной подшипник", "article": "RB-001", "unit": "шт", "quantity": 10, "min_stock": 2, "purchase_price": 2500, "retail_price": 3800, "linked_work": "Замена сцепления"},

        # Подвеска
        {"name": "Амортизатор передний", "article": "SA-001", "unit": "шт", "quantity": 12, "min_stock": 3, "purchase_price": 4500, "retail_price": 6800, "linked_work": "Замена амортизаторов"},
        {"name": "Амортизатор задний", "article": "SA-002", "unit": "шт", "quantity": 12, "min_stock": 3, "purchase_price": 4000, "retail_price": 6000, "linked_work": "Замена амортизаторов"},
        {"name": "Сайлентблок рычага", "article": "SB-001", "unit": "шт", "quantity": 30, "min_stock": 5, "purchase_price": 1200, "retail_price": 1800, "linked_work": "Замена сайлентблоков"},
        {"name": "Шаровая опора", "article": "BJ-001", "unit": "шт", "quantity": 20, "min_stock": 5, "purchase_price": 1800, "retail_price": 2700, "linked_work": ""},
        {"name": "Рулевой наконечник", "article": "TE-001", "unit": "шт", "quantity": 15, "min_stock": 3, "purchase_price": 1500, "retail_price": 2300, "linked_work": ""},

        # Кузовные элементы
        {"name": "Бампер передний", "article": "FB-001", "unit": "шт", "quantity": 3, "min_stock": 1, "purchase_price": 15000, "retail_price": 22000, "linked_work": ""},
        {"name": "Крыло переднее", "article": "FW-001", "unit": "шт", "quantity": 4, "min_stock": 1, "purchase_price": 12000, "retail_price": 18000, "linked_work": ""},
        {"name": "Капот", "article": "HD-001", "unit": "шт", "quantity": 2, "min_stock": 1, "purchase_price": 25000, "retail_price": 38000, "linked_work": ""},
        {"name": "Дверь передняя", "article": "DR-001", "unit": "шт", "quantity": 2, "min_stock": 1, "purchase_price": 18000, "retail_price": 27000, "linked_work": ""},

        # Расходники
        {"name": "Ветошь обтирочная (1кг)", "article": "RG-001", "unit": "кг", "quantity": 50, "min_stock": 10, "purchase_price": 150, "retail_price": 250, "linked_work": ""},
        {"name": "Перчатки нитриловые (100шт)", "article": "GL-001", "unit": "уп", "quantity": 30, "min_stock": 5, "purchase_price": 800, "retail_price": 1200, "linked_work": ""},
        {"name": "Очиститель тормозов (500мл)", "article": "BC-001", "unit": "шт", "quantity": 40, "min_stock": 10, "purchase_price": 350, "retail_price": 550, "linked_work": ""},
        {"name": "Смазка медная (400мл)", "article": "CG-001", "unit": "шт", "quantity": 25, "min_stock": 5, "purchase_price": 500, "retail_price": 800, "linked_work": ""},

        # ЛКМ (лакокрасочные материалы)
        {"name": "Краска автомобильная (1л)", "article": "PT-001", "unit": "шт", "quantity": 15, "min_stock": 3, "purchase_price": 3000, "retail_price": 4500, "linked_work": ""},
        {"name": "Лак автомобильный (1л)", "article": "CL-002", "unit": "шт", "quantity": 15, "min_stock": 3, "purchase_price": 2500, "retail_price": 3800, "linked_work": ""},
        {"name": "Грунт (1л)", "article": "PR-001", "unit": "шт", "quantity": 20, "min_stock": 5, "purchase_price": 1800, "retail_price": 2700, "linked_work": ""},
        {"name": "Шпатлёвка (1кг)", "article": "PT-002", "unit": "шт", "quantity": 25, "min_stock": 5, "purchase_price": 1200, "retail_price": 1800, "linked_work": ""},
        {"name": "Антикор (1л)", "article": "AC-001", "unit": "шт", "quantity": 20, "min_stock": 5, "purchase_price": 1500, "retail_price": 2300, "linked_work": "Антикоррозийная обработка"},
        {"name": "Полироль (500мл)", "article": "PL-001", "unit": "шт", "quantity": 15, "min_stock": 3, "purchase_price": 1800, "retail_price": 2700, "linked_work": "Полировка кузова"},
    ]

    with get_session() as session:
        for part_data in parts_data:
            part = Part(**part_data, is_active=True)
            session.add(part)
        session.commit()
    print(f"✅ Создано {len(parts_data)} позиций запчастей")


def create_demo_performers():
    """Создание демо-исполнителей."""
    print("👷 Создание исполнителей...")

    performers_data = [
        # Mechanical (слесарная группа)
        {"full_name": "Иванов Иван Иванович", "group": "mechanical"},
        {"full_name": "Петров Пётр Петрович", "group": "mechanical"},

        # Repair (ремонтная группа)
        {"full_name": "Сидоров Сидор Сидорович", "group": "repair"},
        {"full_name": "Кузнецов Андрей Викторович", "group": "repair"},

        # Painting (покрасочная группа)
        {"full_name": "Смирнов Алексей Николаевич", "group": "painting"},
        {"full_name": "Фёдоров Игорь Михайлович", "group": "painting"},
    ]

    with get_session() as session:
        for performer_data in performers_data:
            performer = Performer(**performer_data, is_active=True)
            session.add(performer)
        session.commit()
    print(f"✅ Создано {len(performers_data)} исполнителей")


def create_demo_orders():
    """Создание демо-заказов за последние 3 месяца."""
    print("📋 Создание заказов...")

    with get_session() as session:
        clients = session.exec(select(Client)).all()
        works = session.exec(select(Work)).all()
        parts = session.exec(select(Part)).all()
        performers = session.exec(select(Performer)).all()
        masters = session.exec(select(User).where(User.role == "master")).all()

        # Получаем ID работ по именам
        work_map = {w.name: w for w in works}
        part_map = {p.name: p for p in parts}
        performer_map = {p.full_name: p for p in performers}

        orders_count = 0

        # Генерируем заказы за последние 90 дней
        for days_ago in range(90):
            order_date = datetime.now() - timedelta(days=days_ago)

            # 1-2 заказа в день (случайно)
            num_orders_today = random.choice([0, 1, 1, 2])

            for _ in range(num_orders_today):
                client = random.choice(clients)
                vehicles = session.exec(select(Vehicle).where(Vehicle.client_id == client.id)).all()

                if not vehicles:
                    continue

                vehicle = random.choice(vehicles)
                master = random.choice(masters)

                # Статус заказа
                if days_ago < 7:
                    status = random.choice(["draft", "in_progress", "in_progress"])
                elif days_ago < 30:
                    status = random.choice(["in_progress", "completed", "completed", "completed"])
                else:
                    status = "completed"

                # Выбираем работы (1-4 работы)
                num_works = random.randint(1, 4)
                selected_works = random.sample(works, min(num_works, len(works)))

                work_items = []
                total_work_sum = 0

                for work in selected_works:
                    quantity = random.choice([1, 1, 1, 2])  # Обычно 1, иногда 2
                    sum_rub = work.norm_hours * work.rate_rub * quantity

                    work_items.append({
                        "work_id": work.id,
                        "name": work.name,
                        "norm_hours": work.norm_hours,
                        "rate_rub": work.rate_rub,
                        "quantity": quantity,
                        "sum_rub": sum_rub
                    })
                    total_work_sum += sum_rub

                # Добавляем запчасти (0-5 позиций)
                num_parts = random.randint(0, 5)
                material_items = []
                total_material_sum = 0

                if num_parts > 0:
                    selected_parts = random.sample(parts, min(num_parts, len(parts)))

                    for part in selected_parts:
                        quantity = random.randint(1, 3)
                        sum_rub = part.retail_price * quantity

                        material_items.append({
                            "part_id": part.id,
                            "name": part.name,
                            "article": part.article,
                            "quantity": quantity,
                            "unit": part.unit,
                            "price": part.retail_price,
                            "sum_rub": sum_rub
                        })
                        total_material_sum += sum_rub

                # Назначаем исполнителей
                performer_list = []
                salary_dict = {}

                # Для каждой работы назначаем исполнителя из соответствующей группы
                for work_item in work_items:
                    work = work_map.get(work_item["name"])
                    if not work:
                        continue

                    # Находим исполнителей нужной группы
                    group_performers = [p for p in performers if p.group == work.category]
                    if not group_performers:
                        continue

                    performer = random.choice(group_performers)

                    if performer.full_name not in performer_list:
                        performer_list.append(performer.full_name)

                    # Расчёт зарплаты (30% от суммы работ)
                    salary = int(work_item["sum_rub"] * 0.30)
                    salary_dict[performer.full_name] = salary_dict.get(performer.full_name, 0) + salary

                # Генерируем номер заказ-наряда
                zn_number = f"ZN-{order_date.strftime('%y%m%d')}-{orders_count + 1:03d}"

                order = Order(
                    order_id=f"{order_date.strftime('%Y%m%d%H%M%S')}{orders_count:04d}",
                    zn_number=zn_number,
                    vehicle_id=vehicle.id,
                    client_id=client.id,
                    master_id=master.id,
                    status=status,
                    date=order_date.strftime("%d.%m.%Y"),
                    work_items=json.dumps(work_items, ensure_ascii=False),           # 🔥 сериализация
                    material_items=json.dumps(material_items, ensure_ascii=False),   # 🔥 сериализация
                    performer_list=json.dumps(performer_list, ensure_ascii=False),   # 🔥 сериализация
                    salary_dict=json.dumps(salary_dict, ensure_ascii=False),         # 🔥 сериализация
                    draft_notes="",
                    total_amount=total_work_sum + total_material_sum,
                    created_at=order_date
                )

                session.add(order)
                orders_count += 1

        session.commit()
    print(f"✅ Создано {orders_count} заказов")


def main():
    """Главная функция."""
    print("=" * 60)
    print("🚛 TSM Auto — Заполнение базы демо-данными")
    print("=" * 60)
    print()

    # Подтверждение
    print("⚠️  ВНИМАНИЕ: Скрипт удалит все существующие данные (кроме admin)!")
    print()
    response = input("Продолжить? (yes/no): ")

    if response.lower() != "yes":
        print("❌ Отменено пользователем")
        sys.exit(0)

    print()

    try:
        clear_database()
        create_demo_users()
        create_demo_clients()
        create_demo_vehicles()
        create_demo_works()
        create_demo_parts()
        create_demo_performers()
        create_demo_orders()

        print()
        print("=" * 60)
        print("✅ База данных успешно заполнена демо-данными!")
        print("=" * 60)
        print()
        print("📊 Демо-профиль:")
        print("   • 4 пользователя (manager, master1, master2, buh)")
        print("   • 8 клиентов (5 юрлиц + 3 физлица)")
        print("   • 15 автомобилей")
        print("   • 25 видов работ")
        print("   • 40 позиций запчастей")
        print("   • 6 исполнителей")
        print("   • ~50 заказов за 3 месяца")
        print()
        print("🔐 Тестовые аккаунты:")
        print("   • admin / admin123 (администратор)")
        print("   • manager / manager123 (руководитель)")
        print("   • master1 / master123 (мастер)")
        print("   • master2 / master123 (мастер)")
        print("   • buh / buh123 (бухгалтер)")
        print()

    except Exception as e:
        print()
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
