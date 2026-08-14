"""
Модель исполнителя.
"""
from sqlmodel import SQLModel, Field
from typing import Optional


class Performer(SQLModel, table=True):
    __tablename__ = "performers"

    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str = Field(max_length=100)
    group: str = Field(max_length=20)  # mechanical | repair | painting
    is_active: bool = True
