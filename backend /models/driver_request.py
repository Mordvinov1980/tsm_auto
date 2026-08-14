"""Заявки водителей с QR-наклеек."""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class DriverRequest(SQLModel, table=True):
    __tablename__ = "driver_requests"
    id: Optional[int] = Field(default=None, primary_key=True)
    plate: str = Field(max_length=20, index=True)
    phone: str = Field(max_length=20)
    description: str = Field(default="", max_length=500)
    desired_date: str = Field(default="", max_length=20)
    parts: str = Field(default="{}", max_length=1000)  # JSON: {"название": количество}
    status: str = Field(default="new", max_length=20)  # new | called | done
    created_at: datetime = Field(default_factory=datetime.utcnow)