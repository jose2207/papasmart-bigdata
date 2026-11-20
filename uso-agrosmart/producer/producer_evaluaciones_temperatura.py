"""S6 (Mijael): Consumer Kafka telemetría de temperatura -> producer Kafka de evaluaciones de riesgo de helada (simuladas)."""
import json, os, logging
from kafka import KafkaConsumer, KafkaProducer
from decisiones_temperatura import crear_evaluacion

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
KAFKA = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
ORIGEN = os.getenv("TOPICO_TELEMETRIA_TEMP", "agrosmart-u2-temperatura-telemetria")
DESTINO = os.getenv("TOPICO_EMPRESARIAL_TEMP", "agrosmart-u2-temperatura-empresarial")
UMBRAL = float(os.getenv("UMBRAL_HELADA_C", "0"))


def main():
    c = KafkaConsumer(ORIGEN, bootstrap_servers=KAFKA, group_id="agrosmart-derivador-temperatura-v1",
                      auto_offset_reset="earliest", enable_auto_commit=False,
                      value_deserializer=lambda b: json.loads(b.decode("utf-8")))
    p = KafkaProducer(bootstrap_servers=KAFKA, acks="all", retries=5,
                      value_serializer=lambda e: json.dumps(e, ensure_ascii=False).encode("utf-8"))
    try:
        for msg in c:
            try:
                ev = crear_evaluacion(msg.value, UMBRAL)
                r = p.send(DESTINO, key=ev["evento_id"].encode(), value=ev).get(timeout=30)
                c.commit()
                logging.info("Evaluación de helada publicada: telem offset=%s -> empresa offset=%s (%s)", msg.offset, r.offset, ev["estado"])
            except (KeyError, ValueError, TypeError) as exc:
                logging.error("Evento inválido en offset %s: %s", msg.offset, exc); c.commit()
    finally:
        p.flush(); p.close(); c.close()


if __name__ == "__main__":
    main()
