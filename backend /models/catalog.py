# backend/models/catalog.py
"""
Модели каталогов: работы и запчасти.
"""
from sqlmodel import SQLModel, Field
from typing import Optional


class Work(SQLModel, table=True):
    __tablename__ = "works"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=200)   # "Замена масла в двигателе"
    category: str = Field(default="mechanical", max_length=20)   # mechanical | repair | painting
    norm_hours: float = 0.0
    rate_rub: float = 0.0                                        # Ставка руб/час для этой работы
    is_active: bool = True


class Part(SQLModel, table=True):
    __tablename__ = "parts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=200)   # "Нижняя накладка правой фары"
    article: str = Field(default="", max_length=50)              # Артикул
    unit: str = Field(default="шт.", max_length=10)
    quantity: float = 0.0                                        # Текущий остаток на складе
    min_stock: float = 0.0                                       # Минимальный остаток
    purchase_price: float = 0.0                                  # Закупочная цена
    retail_price: float = 0.0                                    # Розничная цена
    linked_work: str = Field(default="", max_length=200)         # Для сопоставления с работой (поле 'from')
    is_active: bool = True
