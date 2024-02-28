# Makefile for managing Django project with Poetry

POETRY = poetry

# Запуск сервера разработки
serve:
	$(POETRY) run python autonews2/manage.py runserver

# Установка зависимостей
install:
	$(POETRY) install

# Применение миграций
migrate:
	$(POETRY) run python autonews2/manage.py migrate

# Запуск тестов
test:
	$(POETRY) run pytest

.PHONY: serve install migrate test
