.PHONY: help install dev test lint docker-up docker-down clean

help:
	@echo "FinAgent Enterprise Development Commands:"
	@echo "  install    - Gerekli bağımlılıkları yükler"
	@echo "  dev        - Backend ve Frontend'i geliştirme modunda başlatır"
	@echo "  test       - Testleri çalıştırır (Backend/Agents)"
	@echo "  lint       - Kod kalitesini denetler (flake8/black)"
	@echo "  docker-up  - Docker konteynerlarını ayağa kaldırır"
	@echo "  docker-down - Konteynerları durdurur"
	@echo "  clean      - Geçici dosyaları temizler"

install:
	pip install -r backend/requirements.txt
	cd frontend && npm install

dev:
	@echo "🚀 Backend başlatılıyor..."
	python3 -m backend.main &
	@echo "🌐 Frontend başlatılıyor..."
	cd frontend && npm run dev

test:
	pytest backend/tests/

lint:
	flake8 backend/
	black backend/ --check

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -f backend/data/audit_logs.jsonl
