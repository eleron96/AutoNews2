# Makefile for managing Django project with Poetry

POETRY = poetry

# Запуск сервера разработки
serve:
	$(POETRY) run python manage.py runserver

# Установка зависимостей
install:
	$(POETRY) install

# Применение миграций
migrate:
	$(POETRY) run python manage.py makemigrations
	$(POETRY) run python manage.py migrate

# Запуск тестов
test:
	$(POETRY) run pytest

.PHONY: serve install migrate test

# Сборка Docker-образа
build-docker:
	docker build -t autonews2:latest .

.PHONY: serve install migrate test build-docker