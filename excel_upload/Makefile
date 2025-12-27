.PHONY: help up down build logs

help:
	@echo "Comandos disponibles:"
	@echo "  make up      - Levanta el proyecto"
	@echo "  make down    - Detiene los contenedores"
	@echo "  make build   - Reconstruye las imágenes"
	@echo "  make logs    - Ver logs"

up:
	docker compose up --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f
