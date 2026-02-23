FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы бота
COPY . .

# Создаем пользователя для безопасности
RUN addgroup --system --gid 1001 botgroup && \
    adduser --system --uid 1001 --gid 1001 --no-create-home botuser && \
    chown -R botuser:botgroup /app

USER botuser

# Команда для запуска бота
CMD ["python", "main.py"]
