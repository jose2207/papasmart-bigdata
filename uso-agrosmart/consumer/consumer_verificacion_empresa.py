"""Comprobación rápida del flujo empresarial simulado: mensajes recientes/históricos."""
import json,os
from kafka import KafkaConsumer
consumer=KafkaConsumer("agrosmart-u2-humedad-empresarial",
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP","kafka:9092"),
    auto_offset_reset="earliest",group_id=None,consumer_timeout_ms=12000,
    value_deserializer=lambda b:json.loads(b.decode("utf-8")))
try:
    for i,m in enumerate(consumer):
        print("TOPIC:",m.topic,"OFFSET:",m.offset,"EVALUACIÓN:",m.value)
        if i>=4: break
finally: consumer.close()
