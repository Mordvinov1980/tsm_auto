# backend/models/vehicle.py
"""
Модель автомобиля клиента.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class Vehicle(SQLModel, table=True):
    __tablename__ = "vehicles"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="clients.id", index=True)
    plate: str = Field(index=True, max_length=20)          # А123АА77
    vin: str = Field(default="", max_length=17)
    brand: str = Field(default="", max_length=50)          # Mercedes-Benz
    model: str = Field(default="", max_length=50)          # Actros MP4
    year: int = 0
    notes: str = Field(default="", max_length=500)
    is_active: bool = True
    
    # Связь с клиентом
    client: "Client" = Relationship(back_populates="vehicles")


from backend.models.client import Client  # noqa
Vehicle.update_forward_refs()
