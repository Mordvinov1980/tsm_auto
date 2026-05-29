"""
Роутер аутентификации.
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlmodel import Session, select

from backend.db import get_session
from backend.models.user import User
from backend.auth import verify_password, create_token, get_current_user
from backend.rate_limit import limiter  # ← ДОБАВЛЕНО

router = APIRouter()


@router.post("/login")
@limiter.limit("5/minute")  # ← ДОБАВЛЕНО: максимум 5 попыток в минуту
async def login(request: Request, body: dict, session: Session = Depends(get_session)):
    """Вход в систему."""
    login = body.get("login", "").strip()
    password = body.get("password", "")

    if not login or not password:
        raise HTTPException(status_code=400, detail="Логин и пароль обязательны")

    user = session.exec(select(User).where(User.login == login, User.is_active == True)).first()

    if not user or not verify_password(password, user.password_hash):
        # Логируем неудачную попытку (опционально)
        client_ip = request.client.host if request.client else "unknown"
        print(f"⚠️  Неудачная попытка входа: {login} с IP {client_ip}")
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    token = create_token(user.id, user.role)

    return {
        "status": "ok",
        "token": token,
        "user": {
            "id": user.id,
            "login": user.login,
            "full_name": user.full_name,
            "role": user.role
        }
    }


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    """Возвращает данные текущего пользователя."""
    db_user = session.exec(select(User).where(User.id == user["user_id"])).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return {
        "status": "ok",
        "user": {
            "id": db_user.id,
            "login": db_user.login,
            "full_name": db_user.full_name,
            "role": db_user.role
        }
    }
