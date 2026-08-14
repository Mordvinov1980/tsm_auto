"""
Загрузка конфигурационных файлов.
"""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"

# Создаём папки, если их нет
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_json(filename: str) -> dict:
    """Загружает JSON-конфиг, возвращает пустой словарь если файла нет."""
    filepath = CONFIG_DIR / filename
    if not filepath.exists():
        return {}
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def save_json(filename: str, data: dict) -> None:
    """Сохраняет JSON-конфиг."""
    filepath = CONFIG_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ========== Конфиги ==========

# Реквизиты компании (редактируются через админ-панель)
contractor_config = load_json("contractor.json")
if not contractor_config:
    contractor_config = {
        "company": "ИП Иванов Иван Иванович",
        "inn": "000000000000",
        "ogrnip": "0000000000000",
        "address": "г. Москва, ул. Примерная, д. 1",
        "email": "info@example.com",
        "phone": "+7 (000) 000-00-00",
        "bank": "ПАО Сбербанк",
        "bik": "044525225",
        "account": "40802810000000000000",
        "corr_account": "30101810400000000225"
    }
    save_json("contractor.json", contractor_config)

# Исполнители и ставки ЗП
performers_config = load_json("performers.json")
if not performers_config:
    performers_config = {
        "groups": {
            "mechanical": ["Иванов", "Петров"],
            "repair": ["Сидоров"],
            "painting": ["Козлов"]
        },
        "salary_rules": {
            "mechanical_rate": 0.30,
            "repair_rate": 0.35,
            "painting_rate": 0.40
        }
    }
    save_json("performers.json", performers_config)

# Email-настройки
email_config = load_json("email.json")
if not email_config:
    email_config = {
        "smtp_server": "smtp.mail.ru",
        "smtp_port": 465,
        "sender_email": "your-email@mail.ru",
        "sender_password": "",
        "recipients": {
            "accounting": "accounting@example.com",
            "personal": "personal@example.com",
            "warehouse": "warehouse@example.com"
        }
    }
    save_json("email.json", email_config)
