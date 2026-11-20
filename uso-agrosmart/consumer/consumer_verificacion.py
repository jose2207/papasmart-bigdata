"""Consumer académico S6/S7: muestra los mensajes de Kafka con sus offsets, en forma legible.

Por defecto lee los ÚLTIMOS N mensajes de cada partición (lo que está llegando ahora).
  --desde inicio  -> lee desde el offset 0 (historia completa)
  --crudo         -> imprime además el JSON completo del mensaje
Humedad: la variable PRINCIPAL es la humedad volumétrica del SUELO (0-1 cm);
la humedad relativa del AIRE (2 m) viaja en el mismo evento solo como dato complementario.
"""
import argparse
import json
import os
from datetime import datetime, timedelta, timezone

from kafka import KafkaConsumer, TopicPartition

TOPICOS = ["agrosmart-u2-humedad-telemetria", "agrosmart-u2-humedad-empresarial",
           "agrosmart-u2-temperatura-telemetria", "agrosmart-u2-temperatura-empresarial"]
LIMA = timezone(timedelta(hours=-5))


def hora_lima(valor):
    """Devuelve la fecha del evento en hora de Lima (acepta ...Z, +00:00 o -05:00)."""
    try:
        dt = datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(LIMA).strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return str(valor)


def linea(topico, v):
    fecha = hora_lima(v.get("fecha_evento"))
    origen = v.get("origen", "?")
    if topico.endswith("humedad-telemetria"):
        aire = v.get("humedad_aire_pct")
        aire_txt = f"   (aire 2 m, complementario: {aire:.1f} %)" if isinstance(aire, (int, float)) else ""
        return (f"{fecha} | HUMEDAD DEL SUELO 0-1 cm = {v.get('humedad_suelo_pct')} %"
                f"{aire_txt} | {v.get('ubicacion', '')} | origen={origen}")
    if topico.endswith("temperatura-telemetria"):
        return f"{fecha} | TEMPERATURA 2 m = {v.get('temperatura_c')} °C | {v.get('ubicacion', '')} | origen={origen}"
    if topico.endswith("humedad-empresarial"):
        return (f"{fecha} | EVALUACIÓN {v.get('tipo', '')} -> estado={v.get('estado')} | "
                f"suelo={v.get('humedad_suelo_pct')} % | umbral={v.get('umbral_demo_pct')} %")
    if topico.endswith("temperatura-empresarial"):
        return (f"{fecha} | EVALUACIÓN {v.get('tipo', '')} -> estado={v.get('estado')} | "
                f"temperatura={v.get('temperatura_c')} °C | umbral helada={v.get('umbral_helada_c')} °C")
    return json.dumps(v, ensure_ascii=False)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--topico", choices=TOPICOS, required=True)
    p.add_argument("--cantidad", type=int, default=5, help="mensajes a mostrar por partición")
    p.add_argument("--desde", choices=["ultimos", "inicio"], default="ultimos")
    p.add_argument("--crudo", action="store_true", help="muestra también el JSON completo")
    a = p.parse_args()
    if a.cantidad < 1:
        p.error("cantidad debe ser > 0")

    c = KafkaConsumer(bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP", "kafka:9092"), group_id=None,
                      enable_auto_commit=False, consumer_timeout_ms=10000,
                      value_deserializer=lambda b: json.loads(b.decode("utf-8")))
    try:
        particiones = [TopicPartition(a.topico, n) for n in sorted(c.partitions_for_topic(a.topico) or [])]
        if not particiones:
            print(f"El tópico {a.topico} no existe o no tiene particiones."); return
        c.assign(particiones)
        inicio, fin = c.beginning_offsets(particiones), c.end_offsets(particiones)
        pendientes = {}
        for tp in particiones:
            desde = inicio[tp] if a.desde == "inicio" else max(inicio[tp], fin[tp] - a.cantidad)
            c.seek(tp, desde)
            pendientes[tp.partition] = min(a.cantidad, fin[tp] - desde)
        print(f"== {a.topico} · {'últimos' if a.desde == 'ultimos' else 'primeros'} {a.cantidad} mensajes · "
              f"offset final actual: {', '.join(f'p{tp.partition}={fin[tp]}' for tp in particiones)} ==")
        for msg in c:
            if pendientes.get(msg.partition, 0) <= 0:
                if all(n <= 0 for n in pendientes.values()):
                    break
                continue
            pendientes[msg.partition] -= 1
            print(f"[offset {msg.offset:>6} · p{msg.partition}] {linea(msg.topic, msg.value)}")
            if a.crudo:
                print("      " + json.dumps(msg.value, ensure_ascii=False))
            if all(n <= 0 for n in pendientes.values()):
                break
    finally:
        c.close()


if __name__ == "__main__":
    main()
