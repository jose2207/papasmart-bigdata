"""Prueba opcional de watermark (Mijael): reenvía una lectura antigua REAL de la API con ID distinto."""
import json, os
from datetime import datetime, timezone
from kafka import KafkaProducer
from open_meteo_temperatura import consultar_api

registros, _ = consultar_api(float(os.getenv("TEMP_LAT", "-14.91")), float(os.getenv("TEMP_LON", "-70.19")), dias=15)
r = registros[-120].copy()
r["evento_id"] += "-tardio-demo"; r["modo_publicacion"] = "replay_historico"
r["emitido_utc"] = datetime.now(timezone.utc).isoformat()
prod = KafkaProducer(bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP", "kafka:9092"),
                     value_serializer=lambda e: json.dumps(e).encode(), acks="all")
try:
    x = prod.send(os.getenv("TOPICO_TELEMETRIA_TEMP", "agrosmart-u2-temperatura-telemetria"), value=r).get(timeout=30)
    print("Evento tardío publicado; offset:", x.offset, "fecha antigua:", r["fecha_evento"], "ID:", r["evento_id"])
finally:
    prod.flush(); prod.close()
