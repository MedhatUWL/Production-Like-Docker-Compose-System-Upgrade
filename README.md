# Production-Like Docker Compose System Upgrade

This repository provides a production-like Docker Compose platform with:

- Traefik reverse proxy (TLS, dashboard, load balancing, rate limiting)
- Frontend + backend pool (`api1`, `api2`)
- Redis cache layer
- MySQL primary + replica topology
- Monitoring (Prometheus, Alertmanager, Grafana, Node Exporter, cAdvisor)
- Centralized logging (Loki + Promtail)
- Automated MySQL backups
- k6 load-testing script

## Architecture

```
Internet
   |
Traefik (80/443/8080)
   |
-----------------------------
|                           |
Frontend                 Backend Pool
                         api1 + api2
                            |
                          Redis
                            |
                     MySQL Primary
                            |
                     MySQL Replica

Monitoring & Logging:
Prometheus, Alertmanager, Grafana, Loki, Promtail, cAdvisor, Node Exporter
```

## Network model

- `public`: internet-facing services (`traefik`, `frontend`)
- `private` (internal): app/data/observability traffic (`api*`, `redis`, `mysql*`, monitoring stack)

## Quick start

1. Copy environment template:

```bash
cp .env.example .env
```

2. Start stack:

```bash
docker compose up -d --build
```

3. Validate:

```bash
docker compose ps
docker network ls
docker network inspect public
docker network inspect private
```

## Main endpoints

- Frontend: `http://app.localhost`
- API health: `http://api.localhost/api/health`
- Traefik dashboard: `http://localhost:8080`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`
- Alertmanager: `http://localhost:9093`

## API key security

The backend requires `X-API-KEY` for `/api/*` routes.

Example:

```bash
curl -i http://api.localhost/api/health
curl -i -H "X-API-KEY: demo-key" http://api.localhost/api/health
```

## Redis cache demo

```bash
docker exec -it redis redis-cli ping
docker logs api1
docker logs api2
```

`/api/data` reads from Redis first; on miss it queries MySQL, then caches the result.

## Backup demo

```bash
ls backups/
```

Backups are generated every 6 hours by `mysql-backup`.

## Load testing

```bash
k6 run k6/test.js
```

## Final demo command set

```bash
docker compose ps
docker ps
docker network ls
docker volume ls
docker stats
docker exec -it redis redis-cli ping
curl -H "X-API-KEY: demo-key" http://api.localhost/api/health
docker logs api1
docker logs api2
ls backups/
k6 run k6/test.js
```
