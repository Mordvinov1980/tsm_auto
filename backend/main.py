"""
TSM Auto API — точка входа.
"""
# ====== 1. ЗАГРУЗКА .env (в самом начале) ======
from pathlib import Path
from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"
if _ENV_FILE.exists():
    load_dotenv(_ENV_FILE)
    print(f"📂 Загружен .env: {_ENV_FILE}")
else:
    print(f"⚠️  .env не найден: {_ENV_FILE}")

# ====== 2. ИМПОРТЫ ======
import os
import sys
import secrets
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from backend.rate_limit import limiter  # ← ЭТА СТРОКА ОБЯЗАТЕЛЬНА
from backend.db import init_db
from backend.routers import (
    auth_router, catalog_router, client_router, performer_router, 
    order_router, admin_router, document_router, report_router, request_router
)

# ====== 3. ПРОВЕРКА БЕЗОПАСНОСТИ ======
ENV_MODE = os.getenv("ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "")

if not SECRET_KEY:
    print("❌ КРИТИЧНО: SECRET_KEY не установлен в .env!")
    print("   Сгенерируйте: python3 -c \"import secrets; print(secrets.token_urlsafe(48))\"")
    sys.exit(1)

if SECRET_KEY in ("change-me-in-production", "tsm-auto-super-secret-key-2026-change-me"):
    if ENV_MODE == "production":
        print("❌ КРИТИЧНО: Используется дефолтный SECRET_KEY в production!")
        sys.exit(1)
    else:
        print("⚠️  ВНИМАНИЕ: Используется дефолтный SECRET_KEY!")

admin_pass = os.getenv("ADMIN_DEFAULT_PASSWORD", "")
if admin_pass and admin_pass in ("admin", "admin123", "password"):
    if ENV_MODE == "production":
        print("⚠️  ВНИМАНИЕ: Слабый ADMIN_DEFAULT_PASSWORD в production!")
    else:
        print(f"ℹ️  ADMIN_DEFAULT_PASSWORD = '{admin_pass}' (смените после первого входа)")

print(f"🚀 Запуск в режиме: {ENV_MODE}")

# ====== 4. ИНИЦИАЛИЗАЦИЯ БД ======
init_db()

# ====== 5. СОЗДАНИЕ FastAPI ПРИЛОЖЕНИЯ ======
app = FastAPI(title="TSM Auto API", version="3.0.0")

# ====== 6. RATE LIMITING (теперь app существует) ======
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)  # ← ВАЖНО: middleware для slowapi

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": f"Слишком много попыток. Подождите {exc.detail}"}
    )

# ====== 🛡️ БЛОКИРОВКА СКАНЕРОВ ======
BLOCK_PATTERNS = [
    # Конфиденциальные файлы (точные совпадения или в начале пути)
    '/.env', '/.git', '/.aws', '/.well-known',
    '/wp-config', '/docker-compose.yml', '/database.yml',
    '/config.php', '/config.js', '/config.json',
    '/settings.php', '/settings.py',
    
    # WordPress (точные пути)
    '/wp-admin', '/wp-includes', '/wp-json', '/wp-login.php',
    '/wlwmanifest.xml', '/xmlrpc.php', '/install.php',
    
    # Laravel / Symfony / Spring (точные пути или с префиксом)
    '/laravel.log', '/telescope', '/_ignition', '/_profiler',
    '/actuator/', '/graphql',
    
    # PHP / Info
    '/phpinfo', '/php_info', '/info.php', '/test.php',
    
    # Прочее
    '/apple-touch-icon', '/robots.txt', '/manifest.json',
    '/gravitysmtp',
    
    
    # iOS/PWA иконки (если не используешь PWA — блокируем)
    '/apple-touch-icon',
    '/apple-touch-icon-precomposed.png',
   
    
]

@app.middleware("http")
async def block_scanners(request: Request, call_next):
    """Возвращает 404 на типичные пути ботов и сканеров уязвимостей."""
    path = request.url.path.lower()
    
    # Проверяем каждый паттерн
    for pattern in BLOCK_PATTERNS:
        pattern_lower = pattern.lower()
        
        # Точное совпадение
        if path == pattern_lower:
            client_ip = request.client.host if request.client else "unknown"
            print(f"🛡️ Заблокирован сканер: {client_ip} → {request.url.path}")
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        
        # Паттерн с префиксом (например, /actuator/ совпадает с /actuator/health)
        if pattern_lower.endswith('/') and path.startswith(pattern_lower):
            client_ip = request.client.host if request.client else "unknown"
            print(f"🛡️ Заблокирован сканер: {client_ip} → {request.url.path}")
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
    
    return await call_next(request)
# ====== /БЛОКИРОВКА СКАНЕРОВ ======

# ====== 8. CORS ======
_origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000")
ALLOWED_ORIGINS = [o.strip() for o in _origins_raw.split(",") if o.strip()]
print(f"🔒 CORS origins: {ALLOWED_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ====== /CORS ======

# Статические файлы (favicon и пр.)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# ========== ПОДКЛЮЧЕНИЕ РОУТЕРОВ ==========
app.include_router(admin_router.router, prefix="/api/admin", tags=["Админ-панель"])
app.include_router(performer_router.router, prefix="/api/performers", tags=["Исполнители"])
app.include_router(auth_router.router, prefix="/api/auth", tags=["Аутентификация"])
app.include_router(catalog_router.router, prefix="/api/catalogs", tags=["Каталоги"])
app.include_router(client_router.router, prefix="/api/clients", tags=["Клиенты"])
app.include_router(order_router.router, prefix="/api/orders", tags=["Заказы"])
app.include_router(document_router.router, prefix="/api/documents", tags=["Документы"])
app.include_router(report_router.router, prefix="/api/reports", tags=["Отчёты"])
app.include_router(request_router.router, prefix="/api/requests", tags=["Заявки"])


# ========== 🏥 HEALTH CHECK ==========
@app.get("/api/health")
async def health_check():
    """Эндпоинт для проверки работоспособности (используется мониторингом)."""
    return {
        "status": "ok", 
        "version": "3.0.0",
        "service": "TSM Auto"
    }


# ========== РАЗДАЧА ФРОНТЕНДА ==========
@app.get("/favicon.ico")
async def favicon():
    """Отдаём SVG как favicon (браузеры это поддерживают)."""
    svg_content = '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="6" fill="#1a1a2e"/>
  <text x="16" y="23" font-size="20" text-anchor="middle" fill="#e94560" font-family="Arial">🚛</text>
</svg>'''
    return Response(content=svg_content, media_type="image/svg+xml")


@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html")


@app.get("/login")
async def serve_login():
    return FileResponse("frontend/login.html")




# ========== ЗАПУСК ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
