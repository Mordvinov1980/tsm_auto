"""
Роутер админ-панели.
"""
from backend.db import get_session
from backend.models.user import User
from backend.auth import hash_password
from sqlmodel import select
from pydantic import BaseModel
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from backend.auth import require_manager  # вместо require_admin
from backend.config import load_json, save_json

router = APIRouter()


@router.get("/settings")
async def get_settings(user: dict = Depends(require_manager)):  # ← здесь
    """Получить все настройки."""
    return {
        "status": "ok",
        "contractor": load_json("contractor.json"),
        "email": {
            "smtp_server": load_json("email.json").get("smtp_server", ""),
            "smtp_port": load_json("email.json").get("smtp_port", 465),
            "sender_email": load_json("email.json").get("sender_email", ""),
            "recipients": load_json("email.json").get("recipients", {})
        },
        "salary_rules": load_json("performers.json").get("salary_rules", {})
    }


@router.put("/settings")
async def update_settings(body: dict, user: dict = Depends(require_manager)):  # ← и здесь
    """Сохранить настройки."""
    if "contractor" in body:
        save_json("contractor.json", body["contractor"])

    if "email" in body:
        email_data = body["email"]
        current_email = load_json("email.json")
        current_email.update(email_data)
        save_json("email.json", current_email)

    if "salary_rules" in body:
        performers = load_json("performers.json")
        performers["salary_rules"] = body["salary_rules"]
        save_json("performers.json", performers)

    return {"status": "ok", "message": "✅ Настройки сохранены"}
    
@router.get("/users")
async def list_users(user: dict = Depends(require_manager)):
    """Получить список всех пользователей системы."""
    with get_session() as session:
        users = session.exec(select(User).order_by(User.id)).all()

    safe_users = []
    for u in users:
        safe_users.append({
            "id": u.id,
            "login": u.login,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
        })

    return {"status": "ok", "users": safe_users, "total": len(safe_users)}
    
class UserCreate(BaseModel):
    login: str
    password: str
    full_name: str
    role: str = "master"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class PasswordChange(BaseModel):
    password: str

@router.post("/users")
async def create_user(body: UserCreate, user: dict = Depends(require_manager)):
    """Создать нового пользователя."""
    VALID_ROLES = {"admin", "manager", "master", "accountant"}
    if body.role not in VALID_ROLES:
        raise HTTPException(400, f"Недопустимая роль. Допустимые: {', '.join(VALID_ROLES)}")
    
    if len(body.password) < 4:
        raise HTTPException(400, "Пароль минимум 4 символа")

    with get_session() as session:
        # Проверяем уникальность логина
        existing = session.exec(select(User).where(User.login == body.login)).first()
        if existing:
            raise HTTPException(400, f"Логин '{body.login}' уже занят")

        new_user = User(
            login=body.login,
            password_hash=hash_password(body.password),
            full_name=body.full_name,
            role=body.role,
            is_active=True,
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        return {
            "status": "ok",
            "message": f"✅ Пользователь '{new_user.login}' создан",
            "user": {
                "id": new_user.id,
                "login": new_user.login,
                "full_name": new_user.full_name,
                "role": new_user.role,
                "is_active": new_user.is_active,
            }
        }


@router.put("/users/{user_id}")
async def update_user(user_id: int, body: UserUpdate, user: dict = Depends(require_manager)):
    """Обновить пользователя (имя, роль, активность)."""
    VALID_ROLES = {"admin", "manager", "master", "accountant"}
    if body.role and body.role not in VALID_ROLES:
        raise HTTPException(400, f"Недопустимая роль. Допустимые: {', '.join(VALID_ROLES)}")

    with get_session() as session:
        target = session.get(User, user_id)
        if not target:
            raise HTTPException(404, "Пользователь не найден")

        # Защита: нельзя деактивировать самого себя
        if body.is_active is False and target.login == user.get("login"):
            raise HTTPException(400, "Нельзя деактивировать свой аккаунт")

        # Защита: нельзя снять роль админа с последнего админа
        if body.role and body.role != "admin" and target.role == "admin":
            admins = session.exec(select(User).where(User.role == "admin", User.is_active == True)).all()
            if len(admins) <= 1:
                raise HTTPException(400, "Нельзя снять роль админа — он последний в системе")

        if body.full_name is not None:
            target.full_name = body.full_name
        if body.role is not None:
            target.role = body.role
        if body.is_active is not None:
            target.is_active = body.is_active

        session.add(target)
        session.commit()

    return {"status": "ok", "message": "✅ Пользователь обновлён"}


@router.put("/users/{user_id}/password")
async def change_user_password(user_id: int, body: PasswordChange, user: dict = Depends(require_manager)):
    """Сменить пароль пользователю."""
    if len(body.password) < 4:
        raise HTTPException(400, "Пароль минимум 4 символа")

    with get_session() as session:
        target = session.get(User, user_id)
        if not target:
            raise HTTPException(404, "Пользователь не найден")

        # Сохраняем login ДО commit (чтобы избежать DetachedInstanceError)
        target_login = target.login
        
        target.password_hash = hash_password(body.password)
        session.add(target)
        session.commit()

    return {"status": "ok", "message": f"✅ Пароль для '{target_login}' изменён"}

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, user: dict = Depends(require_manager)):
    """Деактивировать пользователя."""
    with get_session() as session:
        target = session.get(User, user_id)
        if not target:
            raise HTTPException(404, "Пользователь не найден")

        if target.login == user.get("login"):
            raise HTTPException(400, "Нельзя деактивировать свой аккаунт")

        if target.role == "admin":
            admins = session.exec(select(User).where(User.role == "admin", User.is_active == True)).all()
            if len(admins) <= 1:
                raise HTTPException(400, "Нельзя деактивировать последнего администратора")

        # 🔥 ФИКС: сохраняем login ДО commit
        target_login = target.login

        target.is_active = False
        session.add(target)
        session.commit()

    return {"status": "ok", "message": f"✅ Пользователь '{target_login}' деактивирован"}
