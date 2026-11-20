"""Simulador reproducible de temperatura exterior (°C) para la CARGA INICIAL de la dimensión de Mijael.
Altiplano de Azángaro (~3 900 m): ciclo diario marcado (mínima poco después del amanecer, máxima por la tarde),
ciclo estacional (más frío en jun-jul), anomalías de un día a otro y ruido horario AR(1).
NO son mediciones: cada fila lleva origen='simulado_carga_inicial'.
"""
from __future__ import annotations
import hashlib
from datetime import datetime, timedelta, timezone
import numpy as np

ORIGEN = "simulado_carga_inicial"
UTC_MENOS = 5          # hora local de Perú = UTC-5


def _ciclo_diario(hora_local: float) -> float:
    x = 2 * np.pi * (hora_local - 15.5) / 24.0
    return float((np.cos(x) - 0.30 * np.sin(2 * x)) / 1.14)    # ≈[-1, 1], mínimo ~05h, máximo ~14h locales


def simular(fin_exclusivo: datetime, dias: int = 90, semilla: int = 7, ubicacion: str = "Azángaro") -> list[dict]:
    if dias < 1:
        raise ValueError("dias debe ser >= 1")
    if fin_exclusivo.tzinfo is None:
        fin_exclusivo = fin_exclusivo.replace(tzinfo=timezone.utc)
    fin = fin_exclusivo.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
    n = dias * 24
    inicio = fin - timedelta(hours=n)
    rng = np.random.default_rng(semilla)
    anomalia, ruido, filas, dia_prev = 0.0, 0.0, [], None
    for i in range(n):
        t = inicio + timedelta(hours=i)
        local = t - timedelta(hours=UTC_MENOS)
        if local.date() != dia_prev:                       # nueva anomalía diaria (nubosidad, masas de aire)
            anomalia = 0.7 * anomalia + rng.normal(0, 1.8); dia_prev = local.date()
        doy = t.timetuple().tm_yday
        media = 7.5 + 2.5 * np.cos(2 * np.pi * (doy - 335) / 365.0)      # ~5 °C en junio, ~10 °C en diciembre
        amplitud = 7.5 - 0.5 * np.cos(2 * np.pi * (doy - 335) / 365.0)   # algo mayor en época seca
        ruido = 0.8 * ruido + rng.normal(0, 0.45)
        temp = round(float(np.clip(media + amplitud * _ciclo_diario(local.hour) + anomalia + ruido, -15.0, 30.0)), 1)
        eid = hashlib.sha256(f"simT|{ubicacion}|{t.isoformat()}|{temp:.2f}".encode()).hexdigest()[:32]
        filas.append({"evento_id": eid, "fecha_evento": t.isoformat().replace("+00:00", "Z"),
                      "ubicacion": ubicacion, "temperatura_c": temp, "origen": ORIGEN})
    return filas
