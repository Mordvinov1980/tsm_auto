"""
Rate limiting для защиты от брутфорса.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request


def get_real_ip(request: Request) -> str:
    """Получает реальный IP клиента из заголовков прокси."""
    # Сначала проверяем X-Forwarded-For (цепочка прокси)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Берём первый IP из цепочки (реальный клиент)
        return forwarded_for.split(",")[0].strip()
    
    # Потом X-Real-IP (один IP от Nginx)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback на стандартный метод
    return get_remote_address(request)


limiter = Limiter(key_func=get_real_ip)
