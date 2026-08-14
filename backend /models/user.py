# backend/models/user.py
"""
Модель пользователя.
"""
from sqlmodel import SQLModel, Field
from typing import Optional


class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    login: str = Field(unique=True, index=True, max_length=50)
    password_hash: str
    full_name: str = Field(max_length=100)
    role: str = Field(max_length=20)  # admin | manager | master | accountant
    is_active: bool = True
