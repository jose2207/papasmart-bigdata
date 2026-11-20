"""Cliente Open-Meteo para la DIMENSIÓN DE MIJAEL: temperatura exterior a 2 m (°C), zona de referencia de Azángaro.
Los valores son estimaciones de modelos meteorológicos, NO mediciones de un termómetro físico.
"""
from __future__ import annotations
import hashlib
from datetime import datetime, timezone

from open_meteo_humedad import fecha_utc, guardar_bronze  # reutiliza utilidades comunes

API_URL = "https://api.open-meteo.com/v1/forecast"
HOURLY = "temperature_2m"
ORIGEN = "open_meteo_modelado"


def normalizar(respuesta: dict, ubicacion: str = "Azángaro") -> list[dict]:
    hourly = respuesta.get("hourly") or {}
    if "time" not in hourly or "temperature_2m" not in hourly:
        raise ValueError("Respuesta API incompleta: falta temperature_2m")
    if len(hourly["time"]) != len(hourly["temperature_2m"]):
        raise ValueError("La API devolvió arrays horarios de longitudes distintas")
    salida = []
    for t, temp in zip(hourly["time"], hourly["temperature_2m"]):
        if temp is None:
            continue
        temp = float(temp)
        if not -60.0 <= temp <= 60.0:
            continue
        fecha = fecha_utc(t)
        eid = hashlib.sha256(f"T|{ubicacion}|{fecha}|{temp:.4f}".encode("utf-8")).hexdigest()[:32]
        salida.append({"evento_id": eid, "fecha_evento": fecha, "ubicacion": ubicacion,
                       "temperatura_c": round(temp, 3), "origen": ORIGEN})
    return sorted({(e["fecha_evento"], e["evento_id"]): e for e in salida}.values(), key=lambda e: e["fecha_evento"])


def consultar_api(latitud: float, longitud: float, dias: int = 60, ubicacion: str = "Azángaro", forecast_days: int = 1):
    import requests
    if not 1 <= dias <= 92:
        raise ValueError("past_days debe estar entre 1 y 92")
    res = requests.get(API_URL, params={"latitude": latitud, "longitude": longitud, "hourly": HOURLY,
                                        "past_days": dias, "forecast_days": forecast_days, "timezone": "UTC"}, timeout=60)
    res.raise_for_status()
    cuerpo = res.json()
    registros = normalizar(cuerpo, ubicacion=ubicacion)
    if not registros:
        raise RuntimeError("No se recibieron filas válidas de temperatura de Open-Meteo")
    meta = {"url": res.url, "consultado_utc": datetime.now(timezone.utc).isoformat(),
            "unidades": cuerpo.get("hourly_units", {}), "filas": len(registros),
            "fuente": "Open-Meteo Forecast API; modelos meteorológicos, no termómetros físicos"}
    return registros, meta
