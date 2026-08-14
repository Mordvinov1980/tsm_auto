"""
Бизнес-логика заказов.
"""
import json
import hashlib
from datetime import datetime
from sqlmodel import Session, select

from backend.models.order import Order
from backend.models.catalog import Part, Work
from backend.models.client import Client
from backend.models.vehicle import Vehicle
from backend.db import get_session
from backend.config import performers_config


class OrderService:
    
    def __init__(self):
        self.salary_rules = performers_config.get("salary_rules", {
            "mechanical_rate": 0.30,
            "repair_rate": 0.35,
            "painting_rate": 0.40
        })
    
    def generate_order_id(self) -> str:
        raw = f"{datetime.utcnow().isoformat()}_{id(self)}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]
    
    def create_order(self, data: dict, user_id: int) -> Order:
        with get_session() as session:
            last_order = session.exec(
                select(Order).order_by(Order.id.desc())
            ).first()
            next_zn = str(int(last_order.zn_number) + 1) if last_order else "1"
            
            # work_ids теперь [{id, quantity}, ...]
            work_datas = data.get("work_ids", [])
            work_ids = [wd["id"] for wd in work_datas]
            work_qty_map = {wd["id"]: wd.get("quantity", 1) for wd in work_datas}
            
            works = session.exec(
                select(Work).where(Work.id.in_(work_ids))
            ).all() if work_ids else []
            
            work_items = []
            works_total = 0
            performers_all = set()
            
            performer_groups = data.get("performer_groups", {})
            for group, perfs in performer_groups.items():
                performers_all.update(perfs)
            
            for work in works:
                qty = work_qty_map.get(work.id, 1)
                work_items.append({
                    "name": work.name,
                    "type": work.category,
                    "norm_hours": work.norm_hours,
                    "rate_rub": work.rate_rub,
                    "quantity": qty,
                    "sum_rub": work.norm_hours * work.rate_rub * qty
                })
                works_total += work.norm_hours * work.rate_rub * qty
            
            material_items = []
            materials_total = 0
            
            for mat_data in data.get("material_ids", []):
                part = session.exec(
                    select(Part).where(Part.id == mat_data["id"])
                ).first()
                
                if not part:
                    continue
                
                qty = mat_data.get("quantity", 1)
                if part.quantity >= qty:
                    part.quantity -= qty
                else:
                    qty = part.quantity
                    part.quantity = 0
                
                material_items.append({
                    "name": part.name,
                    "article": part.article,
                    "cost_rub": part.retail_price,
                    "unit": part.unit,
                    "quantity": qty
                })
                materials_total += part.retail_price * qty
            
            total_amount = works_total + materials_total
            
            salary = {p: 0.0 for p in performers_all}
            
            for work in work_items:
                rate = self.salary_rules.get(f"{work['type']}_rate", 0.30)
                
                if work["type"] == "mechanical":
                    target = performer_groups.get("mechanical", [])
                elif work["type"] == "repair":
                    target = performer_groups.get("repair", [])
                elif work["type"] == "painting":
                    target = performer_groups.get("painting", [])
                else:
                    target = list(performers_all)
                
                if not target:
                    continue
                
                share = (work["sum_rub"] * rate) / len(target)
                for p in target:
                    if p in salary:
                        salary[p] += share
            
            order = Order(
                order_id=self.generate_order_id(),
                zn_number=next_zn,
                vehicle_id=data["vehicle_id"],
                client_id=data["client_id"],
                master_id=user_id,
                status="draft",
                date=data.get("date", datetime.now().strftime("%d.%m.%Y")),
                work_items=json.dumps(work_items, ensure_ascii=False),
                material_items=json.dumps(material_items, ensure_ascii=False),
                performer_list=json.dumps(performer_groups, ensure_ascii=False),
                salary_dict=json.dumps(salary, ensure_ascii=False),
                total_amount=total_amount
            )
            
            session.add(order)
            session.commit()
            session.refresh(order)
            
            return order
    
    def get_order(self, order_id: str) -> dict:
        with get_session() as session:
            order = session.exec(
                select(Order).where(Order.order_id == order_id)
            ).first()
            
            if not order:
                return None
            
            return self._order_to_dict(order)
    
    def get_orders(self, filters: dict = None) -> list:
        with get_session() as session:
            statement = select(Order)
            
            if filters:
                if "status" in filters:
                    statement = statement.where(Order.status == filters["status"])
                if "client_id" in filters:
                    statement = statement.where(Order.client_id == filters["client_id"])
                if "date_from" in filters:
                    statement = statement.where(Order.date >= filters["date_from"])
                if "date_to" in filters:
                    statement = statement.where(Order.date <= filters["date_to"])
            
            statement = statement.order_by(Order.created_at.desc())
            orders = session.exec(statement).all()
            
            return [self._order_to_dict(o) for o in orders]
    
    def update_status(self, order_id: str, new_status: str) -> Order:
        with get_session() as session:
            order = session.exec(
                select(Order).where(Order.order_id == order_id)
            ).first()
            
            if not order:
                return None
            
            allowed_transitions = {
                "draft": ["in_progress", "cancelled"],
                "in_progress": ["completed"],
                "completed": [],
                "cancelled": []
            }
            
            if new_status not in allowed_transitions.get(order.status, []):
                raise ValueError(f"Нельзя перевести из '{order.status}' в '{new_status}'")
            
            order.status = new_status
            order.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(order)
            
            return order
    
    def _order_to_dict(self, order: Order) -> dict:
        client_name = "—"
        vehicle_plate = "—"
    
        with get_session() as session:
            client = session.exec(
                select(Client).where(Client.id == order.client_id)
            ).first()
            if client:
                client_name = client.short_name or client.full_name
        
            vehicle = session.exec(
                select(Vehicle).where(Vehicle.id == order.vehicle_id)
            ).first()
            if vehicle:
                vehicle_plate = vehicle.plate
    
        return {
            "id": order.id,
            "order_id": order.order_id,
            "zn_number": order.zn_number,
            "vehicle_id": order.vehicle_id,
            "vehicle_plate": vehicle_plate,
            "client_id": order.client_id,
            "client_name": client_name,
            "master_id": order.master_id,
            "status": order.status,
            "date": order.date,
            "work_items": order.works,
            "material_items": order.materials,
            "performers": order.performers,
            "salary": order.salary,
            "total_amount": order.total_amount,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None,
        }
        
    def delete_order(self, order_id: str) -> bool:
        """Удаляет заказ (только draft) и возвращает запчасти на склад."""
        with get_session() as session:
            order = session.exec(
                select(Order).where(Order.order_id == order_id)
            ).first()
            
            if not order:
                raise ValueError("Заказ не найден")
            
            if order.status != "draft":
                raise ValueError("Можно удалить только черновик")
            
            for mat in order.materials:
                part = session.exec(
                    select(Part).where(Part.name == mat["name"])
                ).first()
                if part:
                    part.quantity += mat.get("quantity", 1)
            
            session.delete(order)
            session.commit()
            return True
