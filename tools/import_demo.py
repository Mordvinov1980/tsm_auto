#!/usr/bin/env python3
"""Импорт демо-профиля в чистую БД TSM Auto v3.0"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.db import init_db, get_session
from backend.models.client import Client
from backend.models.vehicle import Vehicle
from backend.models.catalog import Work, Part
from backend.models.performer import Performer
from backend.models.user import User
from backend.auth import hash_password
from backend.config import save_json
from sqlmodel import select, func

def import_profile(path: str):
    """Импортирует профиль из JSON-файла в БД."""
    print(f"📂 Загрузка профиля: {path}")
    
    with open(path, encoding='utf-8') as f:
        p = json.load(f)
    
    print("🔧 Инициализация БД...")
    init_db()
    
    # Сохраняем JSON-конфиги
    print("⚙️  Сохранение настроек...")
    if p.get("salary_rules"):
        perf_config = {"salary_rules": p["salary_rules"]}
        save_json("performers.json", perf_config)
        print(f"   ✓ Ставки ЗП сохранены")
    
    if p.get("company"):
        save_json("contractor.json", p["company"])
        print(f"   ✓ Реквизиты компании сохранены")
    
    if p.get("email"):
        save_json("email.json", p["email"])
        print(f"   ✓ Настройки email сохранены")
    
    # Импортируем данные в БД
    print("\n📦 Импорт данных в БД...")
    with get_session() as session:
        # Клиенты + авто
        for cdata in p.get('clients', []):
            vehicles = cdata.pop('vehicles', [])
            client = Client(**cdata, is_active=True)
            session.add(client)
            session.flush()
            for vdata in vehicles:
                session.add(Vehicle(
                    client_id=client.id,
                    is_active=True,
                    **vdata
                ))
        
        # Работы
        for wdata in p.get('works', []):
            session.add(Work(**wdata, is_active=True))
        
        # Запчасти
        for pdata in p.get('parts', []):
            session.add(Part(**pdata, is_active=True))
        
        # Исполнители
        for pdata in p.get('performers', []):
            session.add(Performer(**pdata, is_active=True))
        
        # 🔥 Тестовые пользователи
        print("\n👥 Создание тестовых пользователей...")
        test_users = [
            {"login": "manager", "password": "manager123", "full_name": "Смирнов Алексей (Руководитель)", "role": "manager"},
            {"login": "master",  "password": "master123",  "full_name": "Иванов Иван (Мастер-приёмщик)",   "role": "master"},
            {"login": "buh",     "password": "buh123",     "full_name": "Иванова Мария (Бухгалтер)",      "role": "accountant"},
        ]
        
        users_created = 0
        for u in test_users:
            # Проверяем, не существует ли уже такой пользователь
            existing = session.exec(select(User).where(User.login == u["login"])).first()
            if existing:
                print(f"   ⏭  Пользователь '{u['login']}' уже существует, пропуск")
                continue
            
            user = User(
                login=u["login"],
                password_hash=hash_password(u["password"]),
                full_name=u["full_name"],
                role=u["role"],
                is_active=True,
            )
            session.add(user)
            users_created += 1
            print(f"   ✓ Создан: {u['login']} / {u['password']} ({u['role']})")
        
        session.commit()
        
        # Считаем реальное количество из БД
        clients_count = session.exec(select(func.count(Client.id))).one()
        vehicles_count = session.exec(select(func.count(Vehicle.id))).one()
        works_count = session.exec(select(func.count(Work.id))).one()
        parts_count = session.exec(select(func.count(Part.id))).one()
        performers_count = session.exec(select(func.count(Performer.id))).one()
        users_count = session.exec(select(func.count(User.id))).one()
        
        print("\n✅ Импортировано в БД:")
        print(f"   👥 Клиентов: {clients_count}")
        print(f"   🚛 Автомобилей: {vehicles_count}")
        print(f"   🔧 Работ: {works_count}")
        print(f"   📦 Запчастей: {parts_count}")
        print(f"   👷 Исполнителей: {performers_count}")
        print(f"   👤 Пользователей: {users_count} (включая admin)")
        
    print("\n🎉 Готово! Демо-профиль успешно загружен.")
    print("\n📋 Тестовые пользователи:")
    print("   admin   / admin123    — 🛡️ Администратор")
    print("   manager / manager123  — 📋 Руководитель")
    print("   master  / master123   — 🔧 Мастер-приёмщик")
    print("   buh     / buh123      — 💰 Бухгалтер")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python tools/import_demo.py <путь_к_профилю.json>")
        print("Пример: python profiles/demo/demo_profile.json")
        sys.exit(1)
    
    import_profile(sys.argv[1])
