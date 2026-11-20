"""Política DEMOSTRATIVA para eventos de gestión; no es recomendación agronómica."""
from __future__ import annotations
from datetime import datetime, timezone


def crear_evaluacion(telemetria: dict, umbral_demo_pct: float = 20.0) -> dict:
    if not 0 <= umbral_demo_pct <= 100:
        raise ValueError("umbral fuera de rango")
    humedad = float(telemetria["humedad_suelo_pct"])
    if not 0 <= humedad <= 100:
        raise ValueError("humedad fuera de rango")
    return {
        "evento_id": f"eval-{telemetria['evento_id']}",
        "evento_telemetria_id": telemetria["evento_id"],
        "fecha_evento": telemetria["fecha_evento"],
        "ubicacion": telemetria["ubicacion"],
        "tipo": "evaluacion_humedad",
        "estado": "revision_manual" if humedad < umbral_demo_pct else "seguimiento",
        "humedad_suelo_pct": humedad,
        "humedad_aire_pct": float(telemetria["humedad_aire_pct"]),
        "umbral_demo_pct": umbral_demo_pct,
        "origen": "decision_empresarial_simulada_desde_open_meteo",
        "creado_utc": datetime.now(timezone.utc).isoformat(),
    }
