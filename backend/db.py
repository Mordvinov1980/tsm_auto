# backend/db.py (обновлённый)

from sqlmodel import create_engine, SQLModel, Session, select
from sqlalchemy.pool import StaticPool
from sqlalchemy import text
from pathlib import Path

from backend.config import DATA_DIR

DB_PATH = DATA_DIR / "tsm_auto.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def init_db():
    """Создаёт таблицы, включает WAL-режим и добавляет новые колонки."""
    import backend.models.user
    import backend.models.client
    import backend.models.vehicle
    import backend.models.catalog
    import backend.models.order
    import backend.models.document
    import backend.models.performer
    import backend.models.driver_request

    SQLModel.metadata.create_all(engine)

    # WAL-режим
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL;"))
        conn.commit()

    # ===== МИГРАЦИИ (добавление новых колонок) =====
    _migrate_driver_requests()

    _create_default_admin()


def _migrate_driver_requests():
    """Добавляет колонку parts в driver_requests, если её нет."""
    with engine.connect() as conn:
        # Проверяем, есть ли колонка parts
        result = conn.execute(text("PRAGMA table_info(driver_requests);"))
        columns = [row[1] for row in result.fetchall()]
        
        if "parts" not in columns:
            print("🔧 Добавляем колонку parts в driver_requests...")
            conn.execute(text("ALTER TABLE driver_requests ADD COLUMN parts TEXT DEFAULT '{}';"))
            conn.commit()
            print("✅ Колонка parts добавлена")
        else:
            print("ℹ️ Колонка parts уже существует")


def _create_default_admin():
    """Создаёт администратора по умолчанию, если его нет."""
    from backend.models.user import User
    from backend.auth import hash_password
    import os
    
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.login == "admin")).first()
        if not existing:
            admin_password = os.getenv("ADMIN_DEFAULT_PASSWORD", "admin123")
            admin = User(
                login="admin",
                password_hash=hash_password(admin_password),
                full_name="Администратор",
                role="admin",
                is_active=True
            )
            session.add(admin)
            session.commit()
            print("✅ Администратор по умолчанию создан (login: admin)")
        else:
            print("ℹ️ Администратор уже существует")


def get_session():
    """Возвращает новую сессию БД."""
    return Session(engine)