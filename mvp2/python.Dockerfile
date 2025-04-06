FROM python:3.9-slim

WORKDIR /app

# Копируем файлы приложения
COPY requirements.txt .
COPY move_data_to_elastic.py .
COPY password.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Команда по умолчанию
CMD ["python3", "move_data_to_elastic.py"] 