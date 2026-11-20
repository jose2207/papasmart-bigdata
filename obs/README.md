# OBS — Prometheus + Grafana + PostgreSQL exporter

Arranque desde raíz:

```powershell
docker compose --env-file .env -f obs/compose.yml up -d --build
```

- Prometheus: http://localhost:9095/targets.
- Grafana: http://localhost:3300, credenciales `.env`.
- PostgreSQL exporter: http://localhost:9202/metrics.
- Kafka exporter: http://localhost:49309/metrics.
- Datasources automáticos con UIDs `agrosmart_pg`, `agrosmart_prom`.
- Dashboard en `grafana/dashboards/agrosmart_u2.json` (**22 paneles**).
- Alertas en `prometheus/alerts.yml` con reglas de health, heartbeat, microlotes y lag (si existe).

El dashboard usa `Last 90 days` para el replay. Si no aparecen los paneles de costos, ejecuta `costos_pen.py`. Si `UP` es 1 pero el resto muestra `No data`, comprueba que Spark Consumer y los producers ejecutaron, y revisa el rango temporal. Si no llega un nuevo valor horario de Open-Meteo, la falta de eventos no implica fallo.
