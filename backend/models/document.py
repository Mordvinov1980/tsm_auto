# backend/models/document.py
"""
Модель сгенерированного документа.
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Document(SQLModel, table=True):
    __tablename__ = "documents"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", index=True)
    doc_type: str = Field(max_length=20)        # invoice | act | upd | order_narad
    filename: str = Field(max_length=200)       # "25_А123АА77_15-05-2026.xlsx"
    file_path: str = Field(max_length=500)      # /data/documents/25_А123АА77_15-05-2026.xlsx
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: int = Field(foreign_key="users.id")
