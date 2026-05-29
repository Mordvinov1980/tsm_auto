from sqlmodel import create_engine, SQLModel, Session, select
from sqlalchemy.pool import StaticPool  # ← ВОЗВРАЩАЕМ StaticPool
from sqlalchemy import text
from pathlib import Path

from backend.config import DATA_DIR

DB_PATH = DATA_DIR / "tsm_auto.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,       # ← Одно соединение для SQLite
)


def init_db():
    """Создаёт таблицы и включает WAL-режим."""
    import backend.models.user
    import backend.models.client
    import backend.models.vehicle
    import backend.models.catalog
    import backend.models.order
    import backend.models.document
    import backend.models.performer  # noqa

    SQLModel.metadata.create_all(engine)

    # WAL-режим оставляем — он ускоряет чтение
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL;"))
        conn.commit()

    _create_default_admin()


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
