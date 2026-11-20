"""PRODUCER S7: Open-Meteo -> Kafka (replay o seguimiento periódico).
Uso: python producer/producer_api_humedad.py --modo replay --cantidad 72
     python producer/producer_api_humedad.py --modo continuo --intervalo 600
"""
from __future__ import annotations
import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from kafka import KafkaProducer
from open_meteo_humedad import consultar_api, guardar_bronze

TOPICO = os.getenv("TOPICO_TELEMETRIA", "agrosmart-u2-humedad-telemetria")
KAFKA = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
DATOS = Path(os.getenv("DATOS_DIR", "/datos"))
LAT = float(os.getenv("AGRO_LAT", "-15.84"))
LON = float(os.getenv("AGRO_LON", "-70.02"))
UBICACION = os.getenv("AGRO_UBICACION", "Puno")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--modo", choices=["replay", "continuo"], default="replay")
    parser.add_argument("--cantidad", type=int, default=72)
    parser.add_argument("--intervalo", type=float, default=600.0,
                        help="segundos de consulta en modo continuo")
    parser.add_argument("--pausa-evento", type=float, default=0.12,
                        help="segundos entre eventos de una demostración histórica")
    args = parser.parse_args()
    if args.cantidad < 1 or args.intervalo < 60 or args.pausa_evento < 0:
        parser.error("cantidad >=1, intervalo >=60 y pausa-evento >=0")
    DATOS.mkdir(parents=True, exist_ok=True)
    publicados = set()
    # Evita nuevas publicaciones idénticas tras reiniciar el modo continuo.
    seen_path = DATOS / "ids_publicados_continuo.json"
    if args.modo == "continuo" and seen_path.exists():
        publicados = set(json.loads(seen_path.read_text(encoding="utf-8")))
    productor = KafkaProducer(
        bootstrap_servers=KAFKA,
        value_serializer=lambda e: json.dumps(e, ensure_ascii=False).encode("utf-8"),
        acks="all", retries=5,
    )
    try:
        while True:
            registros, meta = consultar_api(LAT, LON, dias=60, ubicacion=UBICACION)
            sello = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            guardar_bronze(DATOS / "bronze" / f"open_meteo_{sello}.json", registros, meta)
            now = datetime.now(timezone.utc)
            # No tratar horas futuras del pronóstico como observaciones ya existentes.
            disponibles = [e for e in registros
                           if datetime.fromisoformat(e["fecha_evento"].replace("Z", "+00:00")) <= now]
            if args.modo == "replay":
                disponibles = disponibles[-args.cantidad:]
            else:
                disponibles = disponibles[-1:]
            for e in disponibles:
                if args.modo == "continuo" and e["evento_id"] in publicados:
                    continue
                e = {**e, "modo_publicacion": "replay_historico" if args.modo == "replay" else "consulta_periodica",
                     "emitido_utc": datetime.now(timezone.utc).isoformat()}
                ack = productor.send(TOPICO, key=e["evento_id"].encode(), value=e).get(timeout=30)
                publicados.add(e["evento_id"])
                print(f"[PRODUCER] {TOPICO} fecha={e['fecha_evento']} offset={ack.offset}", flush=True)
                if args.modo == "replay":
                    time.sleep(args.pausa_evento)
            productor.flush()
            if args.modo == "replay":
                break
            seen_path.write_text(json.dumps(sorted(publicados)[-5000:]), encoding="utf-8")
            time.sleep(args.intervalo)
    finally:
        productor.flush()
        productor.close()


if __name__ == "__main__":
    main()
