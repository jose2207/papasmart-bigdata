"""PRODUCER S7 (Mijael): Open-Meteo temperatura -> Kafka (replay o seguimiento periódico).
Uso: python producer/producer_api_temperatura.py --modo replay --cantidad 72
     python producer/producer_api_temperatura.py --modo continuo --intervalo 600
"""
from __future__ import annotations
import argparse, json, os, time
from datetime import datetime, timezone
from pathlib import Path
from kafka import KafkaProducer
from open_meteo_temperatura import consultar_api, guardar_bronze

TOPICO = os.getenv("TOPICO_TELEMETRIA_TEMP", "agrosmart-u2-temperatura-telemetria")
KAFKA = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
DATOS = Path(os.getenv("DATOS_DIR", "/datos"))
LAT = float(os.getenv("TEMP_LAT", "-14.91"))
LON = float(os.getenv("TEMP_LON", "-70.19"))
UBICACION = os.getenv("TEMP_UBICACION", "Azángaro")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--modo", choices=["replay", "continuo"], default="replay")
    p.add_argument("--cantidad", type=int, default=72)
    p.add_argument("--intervalo", type=float, default=600.0)
    p.add_argument("--pausa-evento", type=float, default=0.12)
    a = p.parse_args()
    if a.cantidad < 1 or a.intervalo < 60 or a.pausa_evento < 0:
        p.error("cantidad >=1, intervalo >=60 y pausa-evento >=0")
    DATOS.mkdir(parents=True, exist_ok=True)
    publicados, seen = set(), DATOS / "ids_publicados_continuo_temperatura.json"
    if a.modo == "continuo" and seen.exists():
        publicados = set(json.loads(seen.read_text(encoding="utf-8")))
    prod = KafkaProducer(bootstrap_servers=KAFKA, acks="all", retries=5,
                         value_serializer=lambda e: json.dumps(e, ensure_ascii=False).encode("utf-8"))
    try:
        while True:
            registros, meta = consultar_api(LAT, LON, dias=60, ubicacion=UBICACION)
            guardar_bronze(DATOS / "bronze" / f"open_meteo_temp_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json", registros, meta)
            ahora = datetime.now(timezone.utc)
            disp = [e for e in registros if datetime.fromisoformat(e["fecha_evento"].replace("Z", "+00:00")) <= ahora]
            disp = disp[-a.cantidad:] if a.modo == "replay" else disp[-1:]
            for e in disp:
                if a.modo == "continuo" and e["evento_id"] in publicados:
                    continue
                e = {**e, "modo_publicacion": "replay_historico" if a.modo == "replay" else "consulta_periodica",
                     "emitido_utc": datetime.now(timezone.utc).isoformat()}
                ack = prod.send(TOPICO, key=e["evento_id"].encode(), value=e).get(timeout=30)
                publicados.add(e["evento_id"])
                print(f"[PRODUCER-TEMP] {TOPICO} fecha={e['fecha_evento']} temp={e['temperatura_c']} offset={ack.offset}", flush=True)
                if a.modo == "replay":
                    time.sleep(a.pausa_evento)
            prod.flush()
            if a.modo == "replay":
                break
            seen.write_text(json.dumps(sorted(publicados)[-5000:]), encoding="utf-8")
            time.sleep(a.intervalo)
    finally:
        prod.flush(); prod.close()


if __name__ == "__main__":
    main()
