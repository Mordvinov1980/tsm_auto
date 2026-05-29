"""Экспорт профиля из БД в JSON."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.db import get_session
from backend.models.client import Client
from backend.models.vehicle import Vehicle
from backend.models.catalog import Work, Part
from backend.models.performer import Performer
from backend.config import load_json
from sqlmodel import select

def export_profile(path: str, comment: str = ""):
    profile = {
        "_comment": comment or "TSM Auto v3.0 Profile",
        "_version": "3.0",
        "_exported": __import__('datetime').datetime.now().isoformat(),
        "clients": [], "works": [], "parts": [], "performers": [],
        "salary_rules": load_json("performers.json").get("salary_rules", {}),
        "company": load_json("contractor.json"),
        "email": load_json("email.json")
    }
    
    # ... остальное без изменений
    
    with get_session() as session:
        for c in session.exec(select(Client)).all():
            vehicles = session.exec(select(Vehicle).where(Vehicle.client_id == c.id)).all()
            profile["clients"].append({
                "full_name": c.full_name, "short_name": c.short_name,
                "inn": c.inn, "kpp": c.kpp, "address": c.address,
                "phone": c.phone, "email": c.email,
                "contact_person": c.contact_person, "notes": c.notes,
                "vehicles": [{"plate": v.plate, "brand": v.brand, "model": v.model, "year": v.year, "vin": v.vin} for v in vehicles]
            })
        
        for w in session.exec(select(Work).where(Work.is_active == True)).all():
            profile["works"].append({"name": w.name, "category": w.category, "norm_hours": w.norm_hours, "rate_rub": w.rate_rub})
        
        for p in session.exec(select(Part).where(Part.is_active == True)).all():
            profile["parts"].append({"name": p.name, "article": p.article, "unit": p.unit, "quantity": p.quantity, "min_stock": p.min_stock, "purchase_price": p.purchase_price, "retail_price": p.retail_price, "linked_work": p.linked_work})
        
        for p in session.exec(select(Performer).where(Performer.is_active == True)).all():
            profile["performers"].append({"full_name": p.full_name, "group": p.group})
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Экспортировано в {path}")
    print(f"   Клиентов={len(profile['clients'])}, Работ={len(profile['works'])}, Запчастей={len(profile['parts'])}, Исполнителей={len(profile['performers'])}")

if __name__ == "__main__":
    export_profile(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "")
