"""Импорт профиля в чистую БД."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.db import init_db, get_session
from backend.models.client import Client
from backend.models.vehicle import Vehicle
from backend.models.catalog import Work, Part
from backend.models.performer import Performer
from backend.config import save_json

def import_profile(path: str):
    with open(path, encoding='utf-8') as f:
        p = json.load(f)
    
    init_db()
    
    # Сохраняем конфиги
    if p.get("salary_rules"):
        perf = {"salary_rules": p["salary_rules"]}
        save_json("performers.json", perf)
    
    if p.get("company"):
        save_json("contractor.json", p["company"])
    
    if p.get("email"):
        save_json("email.json", p["email"])
    
    with get_session() as session:
        # ... остальное без изменений (клиенты, работы, запчасти, исполнители)
        # Клиенты + авто
        for cdata in p.get('clients', []):
            vehicles = cdata.pop('vehicles', [])
            client = Client(**cdata)
            session.add(client)
            session.flush()
            for vdata in vehicles:
                session.add(Vehicle(client_id=client.id, **vdata))
        
        # Работы
        for wdata in p.get('works', []):
            session.add(Work(**wdata, is_active=True))
        
        # Запчасти
        for pdata in p.get('parts', []):
            session.add(Part(**pdata, is_active=True))
        
        # Исполнители
        for pdata in p.get('performers', []):
            session.add(Performer(**pdata, is_active=True))
        
        session.commit()
        
        print(f"✅ Импортировано:")
        print(f"   Клиентов: {len(p.get('clients', []))}")
        print(f"   Работ: {len(p.get('works', []))}")
        print(f"   Запчастей: {len(p.get('parts', []))}")
        print(f"   Исполнителей: {len(p.get('performers', []))}")
        print("🎉 Готово!")

if __name__ == "__main__":
    import_profile(sys.argv[1])
