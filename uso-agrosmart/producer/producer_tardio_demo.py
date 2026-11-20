"""Prueba opcional de watermark: reenvía una estimación antigua con ID distinto.
No se deben usar datos fabricados: toma una lectura histórica obtenida de la API.
"""
import json
import os
from kafka import KafkaProducer
from open_meteo_humedad import consultar_api

registros,_ = consultar_api(float(os.getenv("AGRO_LAT", "-15.84")),
                            float(os.getenv("AGRO_LON","-70.02")),dias=15)
# Aproximadamente cinco días antes del dato más reciente, y un ID nuevo.
r = registros[-120].copy()
r["evento_id"] += "-tardio-demo"
r["modo_publicacion"] = "replay_historico"
from datetime import datetime,timezone
r["emitido_utc"] = datetime.now(timezone.utc).isoformat()
producer=KafkaProducer(bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP","kafka:9092"),
    value_serializer=lambda e:json.dumps(e).encode(),acks="all")
try:
    x=producer.send(os.getenv("TOPICO_TELEMETRIA","agrosmart-u2-humedad-telemetria"),value=r).get(timeout=30)
    print("Evento tardío publicado; offset Kafka:",x.offset,"fecha antigua:",r["fecha_evento"],
          "ID:",r["evento_id"])
finally:producer.flush();producer.close()
