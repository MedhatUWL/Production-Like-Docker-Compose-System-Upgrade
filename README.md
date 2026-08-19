# Production-Like Docker Compose Platform

This repository is a self-contained production-like Compose reference stack:

- Traefik v3 routes the frontend and two API instances and applies rate limiting.
- Traefik exposes HTTP and HTTPS entrypoints and can obtain certificates through Let's Encrypt.
- `public` and internal-only `private` networks isolate data services.
- Redis provides a 60-second API cache; MySQL is seeded with a demo table.
- Prometheus, Alertmanager, Grafana, Loki, Promtail, Node Exporter, and cAdvisor provide metrics, alerts, and logs.
- `mysql-backup` writes compressed-independent SQL dumps every six hours and removes dumps older than seven days.

## Start

```powershell
Copy-Item .env.example .env
# Edit .env and replace every placeholder secret.
docker compose up -d --build
docker compose ps
```

For local use, open `http://localhost`. For a real domain, set `APP_DOMAIN` and `ACME_EMAIL`; create `letsencrypt/acme.json` with mode `600` on Linux before starting. The API health endpoint is public for probes; application data requires the API key:

```powershell
curl http://localhost/api/health
curl -H "X-API-KEY: demo-key" http://localhost/api/items
docker exec -it production-like-redis-1 redis-cli ping
```

The Traefik dashboard is bound to `127.0.0.1:8080`. Grafana is available through `grafana.localhost` when that hostname resolves locally. Prometheus and Alertmanager remain on the private network by design.

## Operations

```powershell
docker compose logs -f api1 api2
docker compose exec redis redis-cli ping
Get-ChildItem backups
docker compose stats
```

Images are pinned to explicit major/minor versions. HTTPS is intentionally left as a deployment configuration: add a DNS name, certificate resolver, and persistent `acme.json` before exposing this stack to the Internet. The included `mysql-replica` is a separate standby data volume; configure binlog replication and a promotion mechanism before calling it automatic failover.

