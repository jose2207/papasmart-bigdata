"""Crea los cuatro tópicos U2 (2 de José: humedad; 2 de Mijael: temperatura), con 1 partición/replica SOLO para el laboratorio."""
import os
import time
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import NoBrokersAvailable

KAFKA = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
NOMBRES = ["agrosmart-u2-humedad-telemetria", "agrosmart-u2-humedad-empresarial",
           "agrosmart-u2-temperatura-telemetria", "agrosmart-u2-temperatura-empresarial"]
admin = None
for intento in range(15):
    try:
        admin=KafkaAdminClient(bootstrap_servers=KAFKA, client_id="agrosmart-init")
        break
    except NoBrokersAvailable:
        time.sleep(2)
if admin is None:
    raise SystemExit("Kafka no está disponible en " + KAFKA)
try:
    existentes=set(admin.list_topics())
    nuevos=[NewTopic(name=x,num_partitions=1,replication_factor=1)
            for x in NOMBRES if x not in existentes]
    if nuevos:
        admin.create_topics(new_topics=nuevos, validate_only=False)
    print("Tópicos:", admin.list_topics())
finally:
    admin.close()
