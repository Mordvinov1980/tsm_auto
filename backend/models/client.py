# backend/models/client.py
"""
Модель клиента.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class Client(SQLModel, table=True):
    __tablename__ = "clients"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str = Field(index=True, max_length=200)       # ООО «Ромашка»
    short_name: str = Field(default="", max_length=100)      # Ромашка
    inn: str = Field(default="", max_length=12)
    kpp: str = Field(default="", max_length=9)
    address: str = Field(default="", max_length=500)
    phone: str = Field(default="", max_length=20)
    email: str = Field(default="", max_length=100)
    contact_person: str = Field(default="", max_length=100)  # Контактное лицо
    notes: str = Field(default="", max_length=1000)
    is_active: bool = True
    
    # История автомобилей клиента
    vehicles: List["Vehicle"] = Relationship(back_populates="client")


from backend.models.vehicle import Vehicle  # noqa (циклический импорт разрешается)
Client.update_forward_refs()
