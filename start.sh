#!/bin/bash
# 🚛 TSM Auto v3.0.7— запуск с туннелем и

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ===== КОНФИГУРАЦИЯ =====
PROJECT_DIR="/home/mordvinov1980/projects/tsm_auto_3.0.7"
SCRIPTS_DIR="/home/mordvinov1980/projects/scripts"
API_PORT=8000
TELEGRAM_SCRIPT="$SCRIPTS_DIR/send_link.py"
LOG_FILE="$PROJECT_DIR/api.log"

# ===== ПРОВЕРКИ =====
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Директория $PROJECT_DIR не найдена${NC}"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/backend/main.py" ]; then
    echo -e "${RED}❌ Файл backend/main.py не найден${NC}"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  Файл .env не найден — используем переменные окружения по умолчанию${NC}"
fi

# 🛑 Очистка при выходе
cleanup() {
    echo -e "\n${YELLOW}🛑 Остановка процессов...${NC}"
    pkill -f "python3 -m backend.main" 2>/dev/null
    pkill -f "localhost.run" 2>/dev/null
    echo -e "${GREEN}✅ Остановлено${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "=========================================="
echo -e "${BLUE}🚛 TSM Auto v3.0${NC}"
echo -e "${BLUE}📁 $PROJECT_DIR${NC}"
echo "=========================================="

# 1. Очистка старых процессов
echo -e "${CYAN}🧹 Очистка старых процессов...${NC}"
pkill -f "python3 -m backend.main" 2>/dev/null
pkill -f "localhost.run" 2>/dev/null
sleep 2

# Ротация лога: старое → api.log.old
if [ -f "$LOG_FILE" ]; then
    mv "$LOG_FILE" "$LOG_FILE.old" 2>/dev/null
fi

# 2. Переход в проект
cd "$PROJECT_DIR" || exit 1

# 3. Активация venv (если есть)
if [ -d "venv" ]; then
    echo -e "${GREEN}🐍 Активация виртуального окружения...${NC}"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${GREEN}🐍 Активация виртуального окружения...${NC}"
    source .venv/bin/activate
fi

# 4. Загрузка .env (если есть)
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

# 5. Запуск API
echo -e "${GREEN}🚀 Запуск API на порту $API_PORT...${NC}"
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port $API_PORT >> "$LOG_FILE" 2>&1 &
API_PID=$!
echo -e "   PID: $API_PID"
sleep 4

# 6. Проверка работоспособности
MAX_RETRIES=5
RETRY=0
while [ $RETRY -lt $MAX_RETRIES ]; do
    if curl -s "http://localhost:$API_PORT" | grep -q "<!DOCTYPE html>"; then
        echo -e "${GREEN}✅ Сервер работает${NC}"
        break
    fi
    RETRY=$((RETRY + 1))
    echo -e "${YELLOW}⏳ Ожидание сервера... ($RETRY/$MAX_RETRIES)${NC}"
    sleep 2
done

if [ $RETRY -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ Сервер не запустился. Последние строки лога:${NC}"
    tail -n 30 "$LOG_FILE"
    pkill -f "python3 -m uvicorn backend.main" 2>/dev/null
    exit 1
fi

# 7. Локальные адреса
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}🌐 Локальный доступ:${NC}"
echo -e "   💻 http://localhost:$API_PORT"
[ -n "$LOCAL_IP" ] && echo -e "   📱 http://$LOCAL_IP:$API_PORT"
echo -e "${BLUE}═══════════════════════════════════════${NC}\n"

# 8. Проверка telegram-скрипта
if [ -f "$TELEGRAM_SCRIPT" ]; then
    echo -e "${GREEN}📤 Telegram-скрипт найден${NC}"
else
    echo -e "${YELLOW}⚠️  Telegram-скрипт не найден: $TELEGRAM_SCRIPT${NC}"
fi

# 9. 🔁 Бесконечный цикл: туннель → разрыв → перезапуск
TUNNEL_URL=""   # ← добавляем переменную для отслеживания уже отправленной ссылки

while true; do
    echo -e "\n${CYAN}🔗 Запуск localhost.run...${NC}"
    TUNNEL_URL=""   # сбрасываем при перезапуске туннеля

    ssh -o ServerAliveInterval=60 \
        -o ServerAliveCountMax=3 \
        -o StrictHostKeyChecking=no \
        -R 80:localhost:$API_PORT \
        localhost.run 2>&1 | while IFS= read -r line; do

        echo "$line"

        # 🔍 Ищем ТОЛЬКО ссылки lhr.life (настоящий туннель)
        if echo "$line" | grep -q "lhr.life tunneled"; then
            URL=$(echo "$line" | grep -oP 'https://[a-z0-9]+\.lhr\.life')

            # Проверяем, что ссылка найдена и не была отправлена ранее
            if [ -n "$URL" ] && [ "$URL" != "$TUNNEL_URL" ]; then
                TUNNEL_URL="$URL"
                echo -e "\n${GREEN}✅ ПУБЛИЧНАЯ ССЫЛКА: $URL${NC}\n"

                # 📤 Отправка в Telegram
                if [ -f "$TELEGRAM_SCRIPT" ]; then
                    python3 "$TELEGRAM_SCRIPT" "$URL" &
                fi

                # 📋 В буфер обмена
                if command -v xclip &>/dev/null; then
                    echo "$URL" | xclip -sel clip
                    echo -e "${GREEN}📋 Скопировано в буфер (xclip)${NC}"
                elif command -v xsel &>/dev/null; then
                    echo "$URL" | xsel --clipboard
                    echo -e "${GREEN}📋 Скопировано в буфер (xsel)${NC}"
                elif command -v pbcopy &>/dev/null; then
                    echo "$URL" | pbcopy
                    echo -e "${GREEN}📋 Скопировано в буфер (pbcopy)${NC}"
                fi
            fi
        fi
    done

    # Туннель упал
    echo -e "${RED}⚠️  Туннель разорван. Перезапуск через 10 сек...${NC}"
    sleep 10
done