# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean

# Устанавливаем pip
RUN pip install --upgrade pip

# Создаем и задаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости проекта
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

# Устанавливаем зависимость django-bootstrap-v5 через pip
RUN pip install django-bootstrap-v5

# Копируем все остальные файлы проекта
COPY . .

# Открываем порт
EXPOSE 8000

# Команда для запуска сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]