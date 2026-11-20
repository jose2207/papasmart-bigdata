"""Comprobación rápida del flujo empresarial de TEMPERATURA (evaluaciones de riesgo de helada simuladas)."""
import json, os
from kafka import KafkaConsumer
c = KafkaConsumer("agrosmart-u2-temperatura-empresarial", bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP", "kafka:9092"),
                  auto_offset_reset="earliest", group_id=None, consumer_timeout_ms=12000,
                  value_deserializer=lambda b: json.loads(b.decode("utf-8")))
try:
    for i, m in enumerate(c):
        print("TOPIC:", m.topic, "OFFSET:", m.offset, "EVALUACIÓN:", m.value)
        if i >= 4: break
finally:
    c.close()
