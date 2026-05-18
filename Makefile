.PHONY: up down logs restart api dashboard psql redis-cli clean

up:
	docker compose -f infra/docker-compose.yml up

up-d:
	docker compose -f infra/docker-compose.yml up -d

down:
	docker compose -f infra/docker-compose.yml down

logs:
	docker compose -f infra/docker-compose.yml logs -f

restart:
	docker compose -f infra/docker-compose.yml restart

api:
	docker compose -f infra/docker-compose.yml logs -f api

dashboard:
	docker compose -f infra/docker-compose.yml logs -f dashboard

psql:
	docker compose -f infra/docker-compose.yml exec postgres psql -U orbisx -d orbisx

redis-cli:
	docker compose -f infra/docker-compose.yml exec redis redis-cli

clean:
	docker compose -f infra/docker-compose.yml down -v
