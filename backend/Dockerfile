# Использование Python 3.11 на Debian slim
FROM python:3.11-slim-bookworm

# Создание каталога приложения
WORKDIR /app

# Создание непривилегированного пользователя (без пароля и домашней директории)
RUN adduser --disabled-password --gecos "" appuser

# Копирование зависимостей и установка
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода под владельца appuser
COPY --chown=appuser:appuser ./app /app/app

# Переключаемся на пользователя appuser
USER appuser

# Указание порта для FastAPI приложения
EXPOSE 8000