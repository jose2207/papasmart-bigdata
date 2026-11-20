"""Simulador reproducible de humedad (SOLO humedad) para la CARGA INICIAL de la Unidad 2.

Genera una serie horaria sintética de humedad del suelo 0-1 cm (%) y humedad relativa del
aire (%) con un patrón calibrado a lo observado en Open-Meteo para Puno:
  * el aire sigue un ciclo diario (máx. de madrugada, mín. por la tarde) + ruido AR(1);
  * el suelo decae hacia una base (~12 %) y sube con "eventos de humedecimiento" aleatorios;
  * los eventos de humedecimiento también elevan la humedad del aire.
NO son mediciones: cada fila lleva origen='simulado_carga_inicial'.
"""
from __future__ import annotations
import hashlib
from datetime import datetime, timedelta, timezone

import numpy as np

ORIGEN = "simulado_carga_inicial"


def simular(fin_exclusivo: datetime, dias: int = 90, semilla: int = 42,
            ubicacion: str = "Puno") -> list[dict]:
    """Serie horaria de `dias` días que termina 1 h antes de `fin_exclusivo` (UTC)."""
    if dias < 1:
        raise ValueError("dias debe ser >= 1")
    if fin_exclusivo.tzinfo is None:
        fin_exclusivo = fin_exclusivo.replace(tzinfo=timezone.utc)
    fin_exclusivo = fin_exclusivo.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
    n = dias * 24
    rng = np.random.default_rng(semilla)
    inicio = fin_exclusivo - timedelta(hours=n)
    base_suelo, exceso, ruido_aire = 12.0, 0.0, 0.0
    filas = []
    for i in range(n):
        t = inicio + timedelta(hours=i)
        if rng.random() < 0.015:                       # evento de humedecimiento
            exceso += rng.exponential(7.0)
        exceso *= 0.95                                 # el efecto se disipa lentamente
        suelo = float(np.clip(base_suelo + exceso + rng.normal(0, 0.05), 6.0, 40.0))
        ruido_aire = 0.85 * ruido_aire + rng.normal(0, 4.0)
        ciclo = 22.0 * np.cos(2 * np.pi * (t.hour - 5) / 24.0)
        aire = float(np.clip(43.0 + ciclo + ruido_aire + 0.8 * exceso, 4.0, 99.0))
        suelo_pct = round(suelo, 1)
        aire_pct = round(aire, 0)
        identidad = f"sim|{ubicacion}|{t.isoformat()}|{suelo_pct:.4f}|{aire_pct:.1f}"
        filas.append({
            "evento_id": hashlib.sha256(identidad.encode()).hexdigest()[:32],
            "fecha_evento": t.isoformat().replace("+00:00", "Z"),
            "ubicacion": ubicacion,
            "humedad_suelo_m3m3": round(suelo_pct / 100.0, 6),
            "humedad_suelo_pct": suelo_pct,
            "humedad_aire_pct": aire_pct,
            "origen": ORIGEN,
            "profundidad_suelo_cm": "0-1",
        })
    return filas
