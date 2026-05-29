"""
JWT-аутентификация и RBAC.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import bcrypt
import os
from functools import wraps

SECRET_KEY = os.getenv("SECRET_KEY", "tsm-auto-super-secret-key-2026-change-me")
ALGORITHM = "HS256"
TOKEN_LIFETIME_HOURS = 24

security = HTTPBearer()


# ========== Пароли ==========

def hash_password(password: str) -> str:
    """Хеширует пароль."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Проверяет пароль."""
    return bcrypt.checkpw(password.encode(), password_hash.encode())


# ========== Токены ==========

def create_token(user_id: int, role: str) -> str:
    """Создаёт JWT-токен с user_id и ролью."""
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_LIFETIME_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Декодирует и проверяет JWT-токен."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Недействительный или истекший токен")


# ========== Зависимости для роутеров ==========

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Извлекает текущего пользователя из токена.
    Используется как зависимость в роутерах.
    """
    return decode_token(credentials.credentials)


def require_roles(*allowed_roles: str):
    """
    Фабрика зависимостей: проверяет, что у пользователя одна из разрешённых ролей.
    
    Использование:
        @router.get("/admin-only")
        async def admin_endpoint(user=Depends(require_roles("admin"))):
            ...
    """
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        return user
    return checker


# Сокращённые зависимости для удобства
require_admin = require_roles("admin")
require_manager = require_roles("admin", "manager")
require_master = require_roles("admin", "manager", "master")
require_accountant = require_roles("admin", "manager", "accountant")
require_any = require_roles("admin", "manager", "master", "accountant")
