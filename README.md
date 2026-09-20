# Production-Like Docker Compose Platform

This repository is a self-contained production-like Compose reference stack:

- Traefik v3 routes the frontend and two API instances and applies rate limiting.
- Traefik exposes HTTP and HTTPS entrypoints and can obtain certificates through Let's Encrypt.
- The API is protected by API key, rate limiting, and a ForwardAuth IP blocklist.
- `public` and internal-only `private` networks isolate data services; only Traefik and the frontend use `public`, while the API is reachable through Traefik over `private`.
- Redis provides a 60-second API cache; MySQL is seeded with a demo table.
- MySQL uses GTID replication with an HAProxy primary-first/fallback router for read traffic.
- Prometheus, Alertmanager, Grafana, Loki, Promtail, Node Exporter, and cAdvisor provide metrics, alerts, and logs.
- MySQL and Blackbox exporters provide database and SSL probe metrics; Prometheus alerts cover downtime, latency, memory, connections, and certificate expiry.
- `mysql-backup` writes compressed-independent SQL dumps every six hours and removes dumps older than seven days.

## Start

```powershell
Copy-Item .env.example .env
# Edit .env and replace every placeholder secret.
docker compose up -d --build
docker compose ps
```

For local use, open `http://localhost`; HTTP redirects to HTTPS. For a real domain, set `APP_DOMAIN` and `ACME_EMAIL`; create `letsencrypt/acme.json` with mode `600` on Linux before starting. The API health endpoint is public for probes; application data requires the API key:

```powershell
curl http://localhost/api/health
curl -H "X-API-KEY: demo-key" http://localhost/api/items
docker exec -it production-like-redis-1 redis-cli ping
```

The Traefik dashboard is bound to `127.0.0.1:8080`. Grafana is available through `grafana.localhost` when that hostname resolves locally. Prometheus and Alertmanager remain on the private network by design.

## Security, Failover, And Load Test

Set `BLOCKED_IPS` in `.env` to a comma-separated list. Requests whose forwarded client IP matches that list receive `403` from Traefik's `api-security` ForwardAuth middleware.

Replication is initialized once the primary and replica are healthy:

```powershell
docker compose up -d mysql-primary mysql-replica mysql-router
docker compose run --rm mysql-replication-init
docker compose exec mysql-replica mysql -uroot -p$env:MYSQL_ROOT_PASSWORD -e "SHOW REPLICA STATUS\\G"
```

The API and backup service use `mysql-router`. HAProxy sends traffic to `mysql-primary` first and promotes the replica backend when the primary TCP health check fails. This is a simple read-failover path; writes require a controlled promotion that disables replica read-only mode.

Run the included k6 test with the load-test profile:

```powershell
docker compose --profile load-test run --rm load-test
```

Application images use `production-like-api:v2` and `production-like-frontend:v2` by default and can be changed through `.env`.

## Operations

```powershell
docker compose logs -f api1 api2
docker compose exec redis redis-cli ping
Get-ChildItem backups
docker compose stats
```

Images are pinned to explicit versions. HTTPS requires a real DNS name, port 80 reachability, and persistent `acme.json`; `localhost` cannot obtain a public Let's Encrypt certificate. The included failover is intentionally primary-first/read-fallback rather than transparent write promotion.

