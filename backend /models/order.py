# backend/models/order.py
"""
Модель заказ-наряда.
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import json


class Order(SQLModel, table=True):
    __tablename__ = "orders"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: str = Field(unique=True, index=True, max_length=50)    # "20260515_143022_abc"
    zn_number: str = Field(max_length=10)                            # "25"
    
    # Внешние ключи
    vehicle_id: int = Field(foreign_key="vehicles.id", index=True)
    client_id: int = Field(foreign_key="clients.id", index=True)
    master_id: int = Field(foreign_key="users.id")                   # Мастер-исполнитель
    
    status: str = Field(default="draft", max_length=20)  # draft | in_progress | completed | cancelled
    date: str = Field(max_length=10)                     # "15.05.2026"
    
    # JSON-поля для гибкого хранения списков
    work_items: str = Field(default="[]")        # [{name, type, norm_hours, rate_rub, quantity, sum_rub}]
    material_items: str = Field(default="[]")     # [{name, cost_rub, unit, quantity}]
    performer_list: str = Field(default="[]")     # ["Иванов", "Петров"]
    salary_dict: str = Field(default="{}")        # {"Иванов": 1500.0}
    draft_notes: str = Field(default="")          # Заметки
    
    total_amount: float = 0.0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # ====== Свойства для работы с JSON ======
    @property
    def works(self) -> list:
        return json.loads(self.work_items)
    
    @works.setter
    def works(self, value: list):
        self.work_items = json.dumps(value, ensure_ascii=False)
    
    @property
    def materials(self) -> list:
        return json.loads(self.material_items)
    
    @materials.setter
    def materials(self, value: list):
        self.material_items = json.dumps(value, ensure_ascii=False)
    
    @property
    def performers(self) -> list:
        return json.loads(self.performer_list)
    
    @performers.setter
    def performers(self, value: list):
        self.performer_list = json.dumps(value, ensure_ascii=False)
    
    @property
    def salary(self) -> dict:
        return json.loads(self.salary_dict)
    
    @salary.setter
    def salary(self, value: dict):
        self.salary_dict = json.dumps(value, ensure_ascii=False)
