"""S6: Consumer Kafka telemetría -> producer Kafka eventos empresariales simulados.
Utiliza exactamente la misma información Open-Meteo; NO genera ventas ni litros inventados.
"""
import json
import os
import logging
from kafka import KafkaConsumer, KafkaProducer
from decisiones import crear_evaluacion

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
KAFKA = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
ORIGEN = os.getenv("TOPICO_TELEMETRIA", "agrosmart-u2-humedad-telemetria")
DESTINO = os.getenv("TOPICO_EMPRESARIAL", "agrosmart-u2-humedad-empresarial")
UMBRAL = float(os.getenv("UMBRAL_SOLO_DEMO_PCT", "20"))


def main():
    consumidor = KafkaConsumer(
        ORIGEN, bootstrap_servers=KAFKA,
        group_id="agrosmart-derivador-humedad-v1",
        auto_offset_reset="earliest", enable_auto_commit=False,
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
    )
    productor = KafkaProducer(
        bootstrap_servers=KAFKA, acks="all", retries=5,
        value_serializer=lambda e: json.dumps(e, ensure_ascii=False).encode("utf-8"),
    )
    try:
        for msg in consumidor:
            try:
                evaluacion = crear_evaluacion(msg.value, UMBRAL)
                r = productor.send(DESTINO, key=evaluacion["evento_id"].encode(), value=evaluacion).get(timeout=30)
                consumidor.commit()  # primero confirma publicación del destino
                logging.info("Evaluación publicada: telem offset=%s, empresa offset=%s", msg.offset, r.offset)
            except (KeyError, ValueError, TypeError) as exc:
                logging.error("Evento inválido en offset %s: %s", msg.offset, exc)
                # No bloquear indefinidamente por datos inválidos en demo; registrar y continuar.
                consumidor.commit()
    finally:
        productor.flush()
        productor.close()
        consumidor.close()


if __name__ == "__main__":
    main()
