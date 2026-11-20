"""Normalización reproducible de la API Open-Meteo. NO son sensores físicos.
La humedad de suelo 0-1 cm se recibe como fracción volumétrica (m³/m³)
y se convierte a porcentaje volumétrico multiplicando por 100.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone

API_URL = "https://api.open-meteo.com/v1/forecast"
HOURLY = "soil_moisture_0_to_1cm,relative_humidity_2m"


def fecha_utc(fecha: str) -> str:
    dt = datetime.fromisoformat(fecha.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def normalizar(respuesta: dict, ubicacion: str = "Puno") -> list[dict]:
    hourly = respuesta.get("hourly") or {}
    claves = ("time", "soil_moisture_0_to_1cm", "relative_humidity_2m")
    if not all(k in hourly for k in claves):
        raise ValueError("Respuesta API incompleta: faltan variables de humedad")
    tamano = len(hourly["time"])
    if any(len(hourly[k]) != tamano for k in claves):
        raise ValueError("La API devolvió arrays horarios de longitudes distintas")
    salida = []
    for t, suelo, aire in zip(*(hourly[k] for k in claves)):
        if suelo is None or aire is None:
            continue
        suelo, aire = float(suelo), float(aire)
        if not (0.0 <= suelo <= 1.0 and 0.0 <= aire <= 100.0):
            continue
        fecha = fecha_utc(t)
        # Los valores forman parte del identificador: una corrección de la API no
        # se confunde con un duplicado exacto de la misma estimación.
        identidad = f"{ubicacion}|{fecha}|{suelo:.8f}|{aire:.4f}"
        eid = hashlib.sha256(identidad.encode("utf-8")).hexdigest()[:32]
        salida.append({
            "evento_id": eid,
            "fecha_evento": fecha,
            "ubicacion": ubicacion,
            "humedad_suelo_m3m3": round(suelo, 6),
            "humedad_suelo_pct": round(suelo * 100.0, 4),
            "humedad_aire_pct": round(aire, 3),
            "origen": "open_meteo_modelado",
            "profundidad_suelo_cm": "0-1",
        })
    # quitar repeticiones exactas de la API conservando orden temporal
    salida = sorted({(e["fecha_evento"], e["evento_id"]): e for e in salida}.values(),
                    key=lambda e: e["fecha_evento"])
    return salida


def consultar_api(latitud: float, longitud: float, dias: int = 60,
                  ubicacion: str = "Puno", forecast_days: int = 1) -> tuple[list[dict], dict]:
    import requests
    if not 1 <= dias <= 92:
        raise ValueError("past_days debe estar entre 1 y 92")
    parametros = {
        "latitude": latitud,
        "longitude": longitud,
        "hourly": HOURLY,
        "past_days": dias,
        "forecast_days": forecast_days,
        "timezone": "UTC",
    }
    res = requests.get(API_URL, params=parametros, timeout=60)
    res.raise_for_status()
    cuerpo = res.json()
    registros = normalizar(cuerpo, ubicacion=ubicacion)
    if not registros:
        raise RuntimeError("No se recibieron filas válidas de humedad de Open-Meteo")
    metadata = {"url": res.url, "consultado_utc": datetime.now(timezone.utc).isoformat(),
                "unidades": cuerpo.get("hourly_units", {}), "filas": len(registros),
                "fuente": "Open-Meteo Forecast API; modelos meteorológicos, no sensores"}
    return registros, metadata


def guardar_bronze(path, registros: list[dict], metadata: dict) -> None:
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"metadata": metadata, "registros": registros},
                            indent=2, ensure_ascii=False), encoding="utf-8")
