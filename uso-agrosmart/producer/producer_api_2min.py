"""PRODUCER S7 · flujo cada 2 minutos (José: humedad · Mijael: temperatura).
Cada 2 min: toma las estimaciones horarias de Open-Meteo (se refrescan cada 10 min), calcula el valor del instante
por interpolación lineal y publica UN evento en Kafka (origen='open_meteo_interpolado_2min').
Uso: python producer/producer_api_2min.py --dimension humedad     |  --dimension temperatura
"""
from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from interpolacion_2min import evento_humedad, evento_temperatura, instante_2min
from kafka import KafkaProducer

KAFKA = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
DATOS = Path(os.getenv("DATOS_DIR", "/datos"))
CONFIG = {
    "humedad": dict(
        lat=float(os.getenv("AGRO_LAT", "-15.84")),
        lon=float(os.getenv("AGRO_LON", "-70.02")),
        ubic=os.getenv("AGRO_UBICACION", "Puno"),
        topico=os.getenv("TOPICO_TELEMETRIA", "agrosmart-u2-humedad-telemetria"),
    ),
    "temperatura": dict(
        lat=float(os.getenv("TEMP_LAT", "-14.91")),
        lon=float(os.getenv("TEMP_LON", "-70.19")),
        ubic=os.getenv("TEMP_UBICACION", "Azángaro"),
        topico=os.getenv("TOPICO_TELEMETRIA_TEMP", "agrosmart-u2-temperatura-telemetria"),
    ),
}


def convertir_a_hora_peru(fecha_utc_str: str) -> str:
    """Convierte un timestamp ISO en UTC (ej. ...Z) a hora de Perú (UTC-5)."""
    dt_utc = datetime.fromisoformat(fecha_utc_str.replace("Z", "+00:00"))
    dt_peru = dt_utc - timedelta(hours=5)
    return dt_peru.strftime("%Y-%m-%dT%H:%M:%S-05:00")


def cargar_api(dim: str, cfg: dict):
    if dim == "humedad":
        from open_meteo_humedad import consultar_api
    else:
        from open_meteo_temperatura import consultar_api
    return consultar_api(cfg["lat"], cfg["lon"], dias=2, ubicacion=cfg["ubic"], forecast_days=2)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dimension", choices=["humedad", "temperatura"], required=True)
    p.add_argument("--intervalo", type=float, default=120.0, help="segundos entre eventos (por defecto 120 = 2 min)")
    p.add_argument("--refresco-api", type=float, default=600.0, help="segundos entre consultas a la API (cache)")
    a = p.parse_args()
    if a.intervalo < 30 or a.refresco_api < 60:
        p.error("intervalo >= 30 s y refresco-api >= 60 s")

    dim, cfg = a.dimension, CONFIG[a.dimension]
    construir = evento_humedad if dim == "humedad" else evento_temperatura
    DATOS.mkdir(parents=True, exist_ok=True)
    marca = DATOS / f"ultimo_2min_{dim}.txt"
    ultimo = datetime.fromisoformat(marca.read_text().strip()) if marca.exists() else None

    prod = KafkaProducer(
        bootstrap_servers=KAFKA,
        acks="all",
        retries=5,
        value_serializer=lambda e: json.dumps(e, ensure_ascii=False).encode("utf-8"),
    )

    registros, t_api = [], None
    print(f"[{dim.upper()}] topico={cfg['topico']} zona={cfg['ubic']} intervalo={a.intervalo:.0f}s", flush=True)

    try:
        while True:
            ahora = datetime.now(timezone.utc)
            if t_api is None or (ahora - t_api).total_seconds() >= a.refresco_api:
                try:
                    registros, _ = cargar_api(dim, cfg)
                    t_api = ahora
                except Exception as exc:
                    print(f"[{dim.upper()}] API no disponible ({exc}); se reutiliza la caché", flush=True)
                    if t_api is None or (ahora - t_api) > timedelta(hours=3):
                        registros = []

            t = instante_2min(ahora, max(1, int(a.intervalo // 60)) if a.intervalo >= 60 else 1)

            if registros and (ultimo is None or t > ultimo):
                e = construir(registros, t, cfg["ubic"])
                if e is not None:
                    e["fecha_evento"] = convertir_a_hora_peru(e["fecha_evento"])
                    e["emitido_utc"] = datetime.now(timezone.utc).isoformat()
                    ack = prod.send(cfg["topico"], key=e["evento_id"].encode(), value=e).get(timeout=30)
                    ultimo = t
                    marca.write_text(t.isoformat())
                    valor = e.get("humedad_suelo_pct", e.get("temperatura_c"))
                    print(f"[{dim.upper()}] fecha={e['fecha_evento']} valor={valor} offset={ack.offset}", flush=True)
                else:
                    print(f"[{dim.upper()}] sin dos anclas horarias consecutivas para {t.isoformat()}", flush=True)

            time.sleep(max(1.0, a.intervalo - (time.time() % a.intervalo)))  # alinea al múltiplo del intervalo
    finally:
        prod.flush()
        prod.close()


if __name__ == "__main__":
    main()