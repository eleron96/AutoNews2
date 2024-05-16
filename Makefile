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
# Извлечение версии из pyproject.toml
VERSION=$(shell grep '^version =' pyproject.toml | sed 's/version = "\(.*\)"/\1/')

# Увеличение версии (предполагается семантическое версионирование)
increment-version:
	@echo "Current version: $(VERSION)"
	@NEW_VERSION=$$(echo $(VERSION) | awk -F. '{print $$1"."$$2"."$$3+1}') && \
	echo "New version: $$NEW_VERSION" && \
	sed -i '' "s/version = \"$(VERSION)\"/version = \"$$NEW_VERSION\"/" pyproject.toml

# Сборка Docker-образа с автоматическим версионированием
build-docker: increment-version
	@NEW_VERSION=$(shell grep '^version =' pyproject.toml | sed 's/version = "\(.*\)"/\1/') && \
	docker build -t autonews2:$$NEW_VERSION -t autonews2:latest .

# Запуск контейнеров с пересборкой
up: build-docker
	docker-compose up -d

# Остановка и удаление контейнеров, сетей и томов
down:
	docker-compose down

# Перезапуск контейнеров
restart: down up

# Просмотр логов контейнеров
logs:
	docker-compose logs -f

# Запуск контейнера вручную
run:
	docker run -it autonews2:latest

# Очищение неиспользуемых образов и других ресурсов
clean:
	docker system prune -f

# Проверка состояния контейнеров
status:
	docker-compose ps


