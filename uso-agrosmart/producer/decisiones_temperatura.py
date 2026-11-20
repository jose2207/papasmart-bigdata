"""Política DEMOSTRATIVA para eventos de gestión de heladas; no es un pronóstico ni alerta oficial (SENAMHI)."""
from __future__ import annotations
from datetime import datetime, timezone


def crear_evaluacion(telemetria: dict, umbral_helada_c: float = 0.0, margen_vigilancia_c: float = 3.0) -> dict:
    temp = float(telemetria["temperatura_c"])
    if not -60.0 <= temp <= 60.0:
        raise ValueError("temperatura fuera de rango")
    if temp <= umbral_helada_c:
        estado = "alerta_helada"
    elif temp <= umbral_helada_c + margen_vigilancia_c:
        estado = "vigilancia"
    else:
        estado = "normal"
    return {"evento_id": f"evalT-{telemetria['evento_id']}", "evento_telemetria_id": telemetria["evento_id"],
            "fecha_evento": telemetria["fecha_evento"], "ubicacion": telemetria["ubicacion"],
            "tipo": "evaluacion_riesgo_helada", "estado": estado, "temperatura_c": temp,
            "umbral_helada_c": umbral_helada_c, "origen": "decision_empresarial_simulada_desde_open_meteo",
            "creado_utc": datetime.now(timezone.utc).isoformat()}
