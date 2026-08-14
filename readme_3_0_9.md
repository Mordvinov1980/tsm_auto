# TSM Auto v3.0

## 🚛 Производственная SPA-система управления автосервисом полного цикла

**© 2026 Олег Мордвинов | Версия: 3.0.9 | Обновлено: 12 августа 2026**

---

## 📌 Обзор системы

**TSM Auto v3.0** — полноценная производственная система для автосервиса грузовых автомобилей. Построена по современным стандартам: REST API на FastAPI, ORM через SQLModel, JWT-аутентификация с RBAC и SPA-фронтенд на Vanilla JS. Решает все задачи автосервиса — от приёма автомобиля до формирования заявок поставщикам и генерации Excel-документов с суммой прописью.

### Ключевые показатели

| Метрика | Значение |
|---------|----------|
| **36** | API эндпоинтов |
| **9** | SQLModel-таблиц |
| **4** | Роли пользователей |
| **7** | Мер безопасности |
| **2** | Сценария развёртывания |
| **1** | Профиль для быстрого старта |
| **1** | Production VPS (tsm-ai.pro) |

### ✅ Ключевые возможности

- 📝 Заказ-наряды с автоматическим расчётом зарплаты исполнителей
- 📦 Складской учёт запчастей с минимальными остатками и автосписанием
- 📤 Автоматические заявки поставщикам по работам «Замена ...»
- 📄 Генерация Excel с реквизитами ИП и суммой прописью
- 🛡️ Полное управление пользователями через админ-панель
- 🎭 Готовый профиль для быстрого развёртывания
- 📱 Мобильный UI с поддержкой iOS Safe Areas
- 🔐 Production-ready безопасность (сканеры, CORS, rate limiting, JWT)
- 📱 **Заявки водителей по QR-коду** — выбор госномера, запчастей, фото

---

## 🏗 Архитектура

### Общая схема

```
КЛИЕНТЫ
  📱 Мастер (телефон)
  💻 Менеджер (ПК)
  💼 Бухгалтер (ПК)
  🚛 Водитель (QR-наклейка)
    ↓
FRONTEND (SPA)
  index.html + login.html (Vanilla JS)
  driver.html (публичная форма для водителей)
    ↓
FASTAPI BACKEND (:8000)
  🛡️ Middleware: Сканеры → CORS → Rate Limit → JWT
    ↓
  10 API-РОУТЕРОВ
    auth • clients • orders • catalogs • requests
    reports • documents • admin • performers • public
    ↓
  БИЗНЕС-ЛОГИКА
    OrderService (заказ + ЗП + склад)
    DocumentService (Excel генерация)
    ↓
СЛОЙ ДАННЫХ
  SQLite (WAL + StaticPool)
  JSON конфиги
  Excel файлы
```

### Структура проекта

```
tsm_auto_prod/
├── backend/
│   ├── main.py                     # Точка входа FastAPI, middleware, роутеры
│   ├── db.py                       # SQLite + WAL + StaticPool + миграции
│   ├── auth.py                     # JWT + bcrypt + RBAC-декораторы
│   ├── rate_limit.py               # SlowAPI limiter
│   ├── config.py                   # Загрузка JSON-конфигов
│   │
│   ├── models/                     # SQLModel-модели (9 таблиц)
│   │   ├── user.py                 # Пользователи системы
│   │   ├── client.py               # Клиенты
│   │   ├── vehicle.py              # Автомобили клиентов
│   │   ├── catalog.py              # Work + Part (работы и запчасти)
│   │   ├── order.py                # Заказ-наряды (JSON-поля)
│   │   ├── document.py             # Сгенерированные документы
│   │   ├── performer.py            # Исполнители работ
│   │   └── driver_request.py       # Заявки водителей с QR ⭐ NEW
│   │
│   ├── routers/                    # 10 API-роутеров
│   │   ├── auth_router.py          # /api/auth/* (login, me)
│   │   ├── client_router.py        # /api/clients/* + /vehicles
│   │   ├── order_router.py         # /api/orders/* + status
│   │   ├── catalog_router.py       # /api/catalogs/works, /parts
│   │   ├── request_router.py       # /api/requests + /recipients + email
│   │   ├── report_router.py        # /api/reports/summary
│   │   ├── document_router.py      # /api/documents/*
│   │   ├── performer_router.py     # /api/performers/*
│   │   ├── admin_router.py         # /api/admin/settings + /users
│   │   └── public_router.py        # /api/public/* (водители) ⭐ NEW
│   │
│   └── services/                   # Бизнес-логика
│       ├── order_service.py        # Заказ + расчёт ЗП + склад
│       └── document_service.py     # Excel через openpyxl + num2words
│
├── frontend/
│   ├── index.html                  # SPA (Vanilla JS, ~200KB)
│   ├── login.html                  # Страница входа
│   └── driver.html                 # Форма для водителей ⭐ NEW
│
├── tools/                          # Миграция и сидирование
│   ├── import_profile.py           # Импорт профиля в БД
│   ├── export_profile.py           # Экспорт БД в JSON
│   ├── seed_data.py                # Начальные данные
│   ├── fix_vehicles.py             # Исправление vehicle_id
│   └── fix_performers.py           # Исправление performer_list
│
├── profiles/                       # Готовые профили
│   └── plastic/
│       └── profile.json            # Plastic Service (демо)
│
├── data/
│   ├── tsm_auto.db                 # SQLite (WAL-режим)
│   └── documents/                  # Сгенерированные Excel
│
├── config/                         # Редактируемые JSON-конфиги
│   ├── contractor.json             # Реквизиты ИП
│   ├── performers.json             # Ставки ЗП исполнителей
│   └── email.json                  # SMTP + получатели
│
├── start.sh                        # Локальный запуск + localhost.run
├── requirements.txt                # Python-зависимости
├── readme.md                       # Эта документация
└── .env                            # Секреты + настройки окружения
```

---

## ⭐ Полный список функций

### 📱 Заявки водителей (QR-наклейки) ⭐ NEW

- ✅ Публичная страница для водителей — `https://tsm-ai.pro/driver`
- ✅ Выбор госномера из базы (без авторизации)
- ✅ Выбор запчастей из каталога (чипсы: тап → +1, ❌ → сброс)
- ✅ Загрузка фото поломки (до 3 шт., до 5 МБ)
- ✅ Автоматическое письмо владельцу с полной информацией
- ✅ Сохранение заявок в БД (`driver_requests`)
- ✅ Статусы: `new` → `called` → `done`
- ✅ Защита от спама: 5 заявок/час с одного IP
- ✅ QR-код для визиток и наклеек на машины

---

### 📝 Заказ-наряды

- ✅ Создание заказа с выбором клиента и авто
- ✅ Ручной ввод клиента/авто с автосозданием в БД
- ✅ Переключение дат стрелками ← → и кнопка "Сегодня"
- ✅ Мультивыбор работ из каталога (тап = +1, крестик = сброс)
- ✅ Мультивыбор запчастей со склада с контролем остатков
- ✅ Назначение исполнителей по 3 группам (механика/ремонт/покраска)
- ✅ Автоматический расчёт зарплаты по ставкам из конфига
- ✅ Статусы: draft → in_progress → completed
- ✅ Поиск заказов по клиенту/госномеру/номеру
- ✅ Фильтр по месяцам с группировкой
- ✅ Удаление черновиков (все роли кроме accountant)
- ✅ Удаление завершённых (только admin)
- ✅ Кнопка «Назад» в просмотре заказа
- ✅ Скачивание Excel с реквизитами и суммой прописью

---

### 👥 Клиенты и авто

- ✅ CRUD клиентов (ФИО, ИНН, КПП, адрес, контакты)
- ✅ Контактные данные и заметки
- ✅ Несколько авто на одного клиента
- ✅ Добавление авто: plate, VIN, brand, model, year
- ✅ Удаление клиента с каскадом на авто (только admin)
- ✅ Поиск по имени, телефону, ИНН
- ✅ История заказов клиента
- ✅ Карточки клиентов с цветными аватарами (инициалы + градиент)

---

### 📦 Склад запчастей

- ✅ Каталог с артикулами и ед. измерения
- ✅ Остатки на складе (количество)
- ✅ Минимальные остатки (min_stock)
- ✅ Закупочная и розничная цена
- ✅ Привязка к работам (linked_work)
- ✅ Авто-списание при создании заказа
- ✅ Поиск по названию
- ✅ Активация/деактивация позиций

---

### 🛠️ Каталог работ

- ✅ 3 категории: mechanical/repair/painting
- ✅ Нормочасы и ставка руб/час
- ✅ Авто-расчёт стоимости работы
- ✅ Группировка по префиксам в UI (Осмотр, Замена, С/у и т.д.)
- ✅ Сворачиваемые подкатегории
- ✅ Активация/деактивация
- ✅ Специальная работа «Осмотр ТС» (выбирается по умолчанию)

---

### 📤 Заявки поставщикам

- ✅ Авто-сбор запчастей за выбранную дату
- ✅ Сопоставление «Замена X» → деталь из каталога
- ✅ Группировка по наименованиям
- ✅ Статистика: позиций, наименований, машин
- ✅ Режим ввода: select ↔ ручной (кнопка ✏️)
- ✅ Навигация по датам (← → Сегодня)
- ✅ Email-отправка через SMTP
- ✅ Множественный выбор получателей (Бухгалтерия/Поставщик/Склад)
- ✅ Предпросмотр заявки перед отправкой
- ✅ Копирование текста заявки в буфер обмена
- ✅ **Защита SMTP-пароля** — мастер получает только список получателей, без пароля

---

### 📄 Документы Excel

- ✅ Генерация через openpyxl
- ✅ Реквизиты ИП из contractor.json
- ✅ Номер заказ-наряда, даты
- ✅ Заказчик + автомобиль
- ✅ Таблица работ с суммами
- ✅ Таблица запчастей с суммами
- ✅ Итоговая сумма
- ✅ Сумма прописью (num2words)
- ✅ Блок подписей
- ✅ Скачивание через Blob (iOS PWA compatible)

---

### 📊 Отчёты и аналитика

- ✅ Сводка за выбранный месяц
- ✅ Количество заказов
- ✅ Общая выручка
- ✅ Средний чек
- ✅ Зарплата по каждому исполнителю
- ✅ Переключение месяцев (← →) и кнопка "Сейчас"
- ✅ Карточки статистики с иконками
- ✅ Детализация по исполнителям (клик → профиль)

---

### 🔧 Исполнители

- ✅ 3 группы: слесарные/ремонтные/покрасочные
- ✅ Индивидуальные ставки ЗП (в % от суммы работ группы)
- ✅ Активация/деактивация
- ✅ Назначение на заказ по группам
- ✅ Автоматический расчёт ЗП при создании заказа
- ✅ Профиль исполнителя с детальной статистикой

---

### 🛡️ Админ-панель (только admin)

- ✅ Редактирование реквизитов ИП
- ✅ Настройка SMTP (сервер, порт, логин)
- ✅ Управление получателями заявок (3 канала)
- ✅ **Управление пользователями:**
  - ✅ Создание новых пользователей (логин, пароль, ФИО, роль)
  - ✅ Редактирование роли и статуса (активен/неактивен)
  - ✅ Смена пароля с подтверждением
  - ✅ Деактивация пользователей (мягкое удаление)
  - ✅ Защита от деактивации себя и последнего админа
  - ✅ Красивые карточки с аватарами
  - ✅ Доступ: **только admin** (руководитель, мастер, бухгалтер не имеют доступа)

---

### 🎨 UI/UX

- ✅ 6 вкладок с iOS segmented control
- ✅ Анимированный ползунок табов
- ✅ **Unified Cards** — единый стиль шапок для всех вкладок (синий градиент)
- ✅ Нижняя context-панель действий с backdrop-blur
- ✅ Карточки с режимами ввода (select ↔ manual)
- ✅ Toast-уведомления (success/error/info)
- ✅ Адаптивность: 320px → 1440px
- ✅ iOS Safe Areas (env(safe-area-inset-bottom))
- ✅ FontAwesome 6 иконки
- ✅ 4 радиуса дизайна (pill/circle/sm/lg)
- ✅ Мобильные карточки для заказов (desktop → table, mobile → cards)
- ✅ **Приглушённая светлая палитра** (глаза не устают)
- ✅ **4 градиента аватаров** (вместо 7 кислотных)

---

## 🛡️ Безопасность (production-ready)

В v3.0.9 реализован комплексный подход к безопасности — **7 независимых слоёв защиты**.

### ✅ 1. Блокировка сканеров

Middleware возвращает 404 на типичные пути ботов: `/.env`, `/wp-admin`, `/actuator`, `/.git`, `/phpinfo` и др. (30+ паттернов). Логирует IP нарушителя.

**Пример из логов:**
```
INFO: 37.19.76.199:0 - "GET /wp-admin HTTP/1.0" 404 Not Found
INFO: 37.19.76.199:0 - "GET /.env HTTP/1.0" 404 Not Found
INFO: 37.19.76.199:0 - "GET /actuator/health HTTP/1.0" 404 Not Found
```

### ✅ 2. CORS whitelist

Вместо `["*"]` — строгий список разрешённых доменов из переменной `CORS_ORIGINS`. Защита от CSRF-атак и несанкционированного доступа с других сайтов.

**Конфигурация:**
```bash
CORS_ORIGINS=https://tsm-ai.pro,http://localhost:8000,http://127.0.0.1:8000
```

### ✅ 3. JWT + bcrypt

Токены с 24-часовым TTL, подписанные криптографическим HMAC-SHA256 ключом. Пароли хешируются через bcrypt с солью. Поддержка 4 ролей в токене.

**Пример токена:**
```json
{
  "user_id": 1,
  "role": "admin",
  "exp": 1717848000
}
```

### ✅ 4. Rate limiting (SlowAPI)

Эндпоинты `/api/auth/login` и `/api/public/request` ограничены **5 попытками в минуту** с одного IP. Защита от брутфорса и спама.

**Пример из логов:**
```
INFO: 37.19.76.199:0 - "POST /api/auth/login HTTP/1.0" 401 Unauthorized
INFO: 37.19.76.199:0 - "POST /api/auth/login HTTP/1.0" 429 Too Many Requests
```

### ✅ 5. Проверка JWT_SECRET

При старте приложение проверяет наличие и стойкость `SECRET_KEY`. В production-режиме запуск с дефолтным ключом невозможен — приложение падает с ошибкой.

### ✅ 6. WAL-режим SQLite

Write-Ahead Logging для параллельного чтения/записи без блокировок. Плюс `PRAGMA synchronous=NORMAL` и кеш 64MB.

### ✅ 7. Health endpoint

`GET /api/health` для мониторинга через systemd, UptimeRobot или другие системы. Публичный, без авторизации.

---

### Конфигурация безопасности в `.env`

```bash
# === КРИТИЧНЫЕ СЕКРЕТЫ ===
SECRET_KEY=
ADMIN_DEFAULT_PASSWORD=    # сменить после первого входа!

# === ОКРУЖЕНИЕ ===
ENV=development                       # или production на VPS

# === CORS (список через запятую) ===
CORS_ORIGINS=https://tsm-ai.pro,http://localhost:8000,http://127.0.0.1:8000,http://192.168.1.165:8000

# === БД ===
DATABASE_URL=sqlite:///data/tsm_auto.db
```

---

## 🗄 Схема базы данных

### ER-диаграмма

```
USERS
  id (PK)
  login (UK)
  password
  full_name
  role (admin/manager/master/accountant)
  is_active
    ↓ master_id
ORDERS
  id (PK)
  order_id
  zn_number
  vehicle_id ──→ VEHICLES
  client_id ──→ CLIENTS
  master_id ──→ USERS
  status
  date
  work_items (JSON)
  material_items (JSON)
  performers (JSON)
  salary (JSON)
  total_amount
    ↓ client_id
CLIENTS
  id (PK)
  full_name
  short_name
  inn
  kpp
  address
  phone
  email
  contact_person
  notes
    ↓ client_id
VEHICLES
  id (PK)
  client_id (FK)
  plate
  vin
  brand
  model
  year
    ↓ order_id
DOCUMENTS
  id (PK)
  order_id (FK)
  doc_type
  filename
  file_path
  generated_at
```

### Таблицы каталогов

```
WORKS
  id (PK)
  name
  category (mechanical/repair/painting)
  norm_hours
  rate_rub
  is_active

PARTS
  id (PK)
  name
  article
  unit
  quantity
  min_stock
  purchase_price
  retail_price
  linked_work
  is_active

PERFORMERS
  id (PK)
  full_name
  group (mechanical/repair/painting)
  is_active
```

### Таблица заявок водителей ⭐ NEW

```
DRIVER_REQUESTS
  id (PK)
  plate (INDEX)        # госномер
  phone                # телефон водителя
  description          # описание поломки
  desired_date         # дата приезда
  parts (JSON)         # {"название": количество}
  status               # new | called | done
  created_at
```

---

## ⚙️ API Reference (36 эндпоинтов)

### 🔐 Аутентификация

| Метод | Эндпоинт | Описание | Доступ |
|-------|----------|----------|--------|
| POST | `/api/auth/login` | Вход в систему | 🚦 5/min |
| GET | `/api/auth/me` | Текущий пользователь | JWT |

### 👥 Клиенты и авто

| Метод | Эндпоинт | Описание | Доступ |
|-------|----------|----------|--------|
| GET | `/api/clients` | Список клиентов | Все |
| POST | `/api/clients` | Создать клиента | master+ |
| GET | `/api/clients/{id}` | Детали клиента | Все |
| PUT | `/api/clients/{id}` | Обновить клиента | master+ |
| DELETE | `/api/clients/{id}` | Удалить клиента | admin |
| POST | `/api/clients/{id}/vehicles` | Добавить авто | master+ |
| DELETE | `/api/clients/{cid}/vehicles/{vid}` | Удалить авто | admin |

### 📋 Заказы

| Метод | Эндпоинт | Описание | Доступ |
|-------|----------|----------|--------|
| GET | `/api/orders` | Список заказов | Все |
| POST | `/api/orders` | Создать заказ | master+ |
| GET | `/api/orders/{id}` | Детали заказа | Все |
| PUT | `/api/orders/{id}/status` | Сменить статус | master+ |
| DELETE | `/api/orders/{id}` | Удалить заказ | draft: все, completed: admin |

### 🛠️ Каталоги

| Метод | Эндпоинт | Описание | Доступ |
|-------|----------|----------|--------|
| GET | `/api/catalogs/works` | Список работ | Все |
| POST | `/api/catalogs/works` | Создать работу | manager+ |
| DELETE | `/api/catalogs/works/{id}` | Удалить работу | manager+ |
| GET | `/api/catalogs/parts` | Список запчастей | Все |
| POST | `/api/catalogs/parts` | Создать запчасть | manager+ |
| DELETE | `/api/catalogs/parts/{id}` | Удалить запчасть | manager+ |

### 🔧 Исполнители

| Метод | Эндпоинт | Описание | Доступ |
|-------|----------|----------|--------|
| GET | `/api/performers` | Список исполнителей | Все |
| POST | `/api/performers` | Создать исполнителя | manager+ |
| DELETE | `/api/performers/{id}` | Удалить исполнителя | manager+ |

### 📦 Заявки на запчасти

| Метод | Эндпоинт | Описание | Доступ |
|-------|----------|----------|--------|
| GET | `/api/requests?date=ДД.ММ.ГГГГ` | Заявки за дату | master+ |
| GET | `/api/requests/recipients` | Получатели (без SMTP-пароля) | master+ |
| POST | `/api/requests/send-email` | Отправить на email | master+ |

### 📱 Публичные эндпоинты для водителей ⭐ NEW

| Метод | Эндпоинт | Описание | Доступ |
|-------|----------|----------|--------|
| GET | `/api/public/vehicles` | Список госномеров | Public |
| GET | `/api/public/parts` | Список запчастей | Public |
| POST | `/api/public/request` | Отправить заявку с фото | 🚦 5/hour |

### 📊 Отчёты

| Метод | Эндпоинт | Описание | Доступ |
|-------|----------|----------|--------|
| GET | `/api/reports/summary?month=&year=` | Сводка за месяц | Все |

### 📄 Документы

| Метод | Эндпоинт | Описание | Доступ |
|-------|----------|----------|--------|
| POST | `/api/documents/order/{id}` | Генерация Excel | Все |
| GET | `/api/documents/download/{file}` | Скачивание файла | Все |

### ⚙️ Админка (только admin)

| Метод | Эндпоинт | Описание | Доступ |
|-------|----------|----------|--------|
| GET | `/api/admin/settings` | Получить настройки | admin |
| PUT | `/api/admin/settings` | Сохранить настройки | admin |
| GET | `/api/admin/users` | Список пользователей | admin |
| POST | `/api/admin/users` | Создать пользователя | admin |
| PUT | `/api/admin/users/{id}` | Обновить пользователя | admin |
| PUT | `/api/admin/users/{id}/password` | Сменить пароль | admin |
| DELETE | `/api/admin/users/{id}` | Деактивировать пользователя | admin |

### 🏥 Мониторинг

| Метод | Эндпоинт | Описание | Доступ |
|-------|----------|----------|--------|
| GET | `/api/health` | Проверка здоровья | Public |

> ⚠️ Все эндпоинты (кроме `/api/auth/login`, `/api/health`, `/`, `/login`, `/api/public/*`, `/driver`) требуют заголовок `Authorization: Bearer <JWT>`.

---

## 🚀 Два сценария развёртывания

### Сценарий A: VPS (24/7, HTTPS)

| Компонент | Конфигурация |
|-----------|--------------|
| **ОС** | Ubuntu 26.04 LTS |
| **Python** | 3.12 (pyenv) |
| **Веб-сервер** | Nginx 1.28+ (reverse proxy) |
| **SSL** | Let's Encrypt + авто-продление |
| **Менеджер процессов** | systemd (Restart=always) |
| **Домен** | https://tsm-ai.pro |

**systemd unit:** `/etc/systemd/system/tsm-auto.service`

```ini
[Unit]
Description=TSM Auto v3.0
After=network.target

[Service]
Type=simple
User=tsm
WorkingDirectory=/home/tsm/tsm_auto_prod
EnvironmentFile=/home/tsm/tsm_auto_prod/.env
ExecStart=/home/tsm/tsm_auto_prod/venv/bin/uvicorn backend.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --proxy-headers \
    --forwarded-allow-ips="127.0.0.1"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

> ⚠️ **Важно:** Флаги `--proxy-headers` и `--forwarded-allow-ips` нужны, чтобы uvicorn видел реальные IP клиентов из заголовка `X-Forwarded-For`, а не `127.0.0.1`. Без них rate limiting будет блокировать всех пользователей разом.

### Сценарий B: Локально в автосервисе

Установка на ноутбук в автосервисе. Сотрудники работают в локальной сети.

---

## 📝 Changelog

### v3.0.9 (12 августа 2026) — 📱 QR-заявки для водителей

- ✅ **Новый модуль: заявки водителей по QR-коду**
  - Публичная страница `/driver` с формой для водителей
  - Выбор госномера из БД (эндпоинт `/api/public/vehicles`)
  - Выбор запчастей из каталога (чипсы с инкрементом и ❌)
  - Загрузка фото поломки (до 3 шт., до 5 МБ)
  - Автоматическое письмо на почту с текстом и вложениями
  - Сохранение в БД (`driver_requests` с полем `parts`)
  - Автоматическая миграция БД (добавление колонки `parts`)
- ✅ **Новая таблица:** `driver_requests` (заявки водителей)
- ✅ **Новый роутер:** `public_router.py` (публичные эндпоинты)
- ✅ **Новые эндпоинты:** `/api/public/vehicles`, `/api/public/parts`, `/api/public/request`
- ✅ **Защита от спама:** 5 заявок/час с одного IP (через SlowAPI)
- ✅ **Обновлён `db.py`:** автоматическое добавление новых колонок при старте

### v3.0.8 (7 июня 2026)

#### 🛡️ Production-hardening на VPS (tsm-ai.pro)
- ✅ Защита скачивания Excel через JWT
- ✅ Rate limiting по реальному IP
- ✅ Nginx + systemd с флагами `--proxy-headers`
- ✅ Расширение блокировки сканеров
- ✅ Фиксы стабильности

### v3.0.7 (29-30 мая 2026)

#### 🎭 Демо-профиль для быстрого старта
- ✅ `data/demo_profile.json` — реалистичный профиль автосервиса
- ✅ `tools/import_demo.py` — скрипт импорта
- ✅ **UI/UX:** Unified Cards, приглушённая палитра, 4 градиента аватаров
- ✅ **Разделение прав:** только admin имеет доступ к админке

---

**TSM Auto v3.0.9** | Обновлено: 12 августа 2026
© 2026 Олег Мордвинов | Production-ready SPA-система для автосервиса

**FastAPI + SQLModel + JWT + RBAC + Demo Profile + Unified Cards + Production Security + QR-заявки**
