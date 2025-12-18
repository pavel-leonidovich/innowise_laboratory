FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .

RUN pip install -r requirements.txt


# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY . .

# Открываем порт
EXPOSE 8000

# Запускаем приложение
#CMD ["ls"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
