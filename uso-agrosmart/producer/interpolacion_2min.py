"""Serie de 2 minutos ANCLADA en estimaciones horarias reales de Open-Meteo (humedad y temperatura).

Open-Meteo entrega estimaciones de MODELO con paso horario (la humedad del suelo no existe a menor resolución):
ninguna API pública gratuita publica humedad del suelo observada cada 2 minutos para Puno/Azángaro. Para tener un
flujo en vivo cada 2 min, el valor de cada instante se calcula por INTERPOLACIÓN LINEAL entre las dos estimaciones
horarias que lo rodean. Es una reconstrucción determinista (no agrega ruido ni inventa variaciones) y cada evento se
etiqueta origen='open_meteo_interpolado_2min'. NO es una medición de sensor.
"""
from __future__ import annotations
import hashlib
from bisect import bisect_right
from datetime import datetime, timedelta, timezone

ORIGEN = "open_meteo_interpolado_2min"
MODO = "interpolado_2min"


def a_utc(texto: str) -> datetime:
    dt = datetime.fromisoformat(texto.replace("Z", "+00:00"))
    return (dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt).astimezone(timezone.utc)


def instante_2min(ahora: datetime, paso_min: int = 2) -> datetime:
    """Redondea hacia abajo a la rejilla de `paso_min` minutos (UTC)."""
    ahora = ahora.astimezone(timezone.utc).replace(second=0, microsecond=0)
    return ahora - timedelta(minutes=ahora.minute % paso_min)


def interpolar(registros: list[dict], t: datetime, campos: list[str]):
    """Interpola `campos` en el instante `t` entre dos horas CONSECUTIVAS. Devuelve (valores, hora_a, hora_b, peso) o None."""
    if not registros:
        return None
    fechas = [a_utc(r["fecha_evento"]) for r in registros]
    i = bisect_right(fechas, t) - 1
    if i < 0 or i + 1 >= len(registros):
        return None
    ta, tb = fechas[i], fechas[i + 1]
    if tb - ta != timedelta(hours=1):          # no interpolar a través de huecos
        return None
    peso = (t - ta).total_seconds() / 3600.0
    ra, rb = registros[i], registros[i + 1]
    return {c: ra[c] + peso * (rb[c] - ra[c]) for c in campos}, ta, tb, peso


def _id(prefijo: str, ubicacion: str, fecha: str, *valores: float) -> str:
    base = "|".join([prefijo, ubicacion, fecha] + [f"{v:.6f}" for v in valores])
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:32]


def evento_humedad(registros: list[dict], t: datetime, ubicacion: str):
    r = interpolar(registros, t, ["humedad_suelo_pct", "humedad_aire_pct"])
    if r is None:
        return None
    v, ta, tb, peso = r
    suelo, aire = round(v["humedad_suelo_pct"], 4), round(v["humedad_aire_pct"], 3)
    if not (0.0 <= suelo <= 100.0 and 0.0 <= aire <= 100.0):
        return None
    fecha = t.isoformat().replace("+00:00", "Z")
    return {"evento_id": _id("i2h", ubicacion, fecha, suelo, aire), "fecha_evento": fecha, "ubicacion": ubicacion,
            "humedad_suelo_m3m3": round(suelo / 100.0, 6), "humedad_suelo_pct": suelo, "humedad_aire_pct": aire,
            "origen": ORIGEN, "profundidad_suelo_cm": "0-1", "modo_publicacion": MODO,
            "ancla_hora_a": ta.isoformat().replace("+00:00", "Z"), "ancla_hora_b": tb.isoformat().replace("+00:00", "Z"),
            "peso_interpolacion": round(peso, 4)}


def evento_temperatura(registros: list[dict], t: datetime, ubicacion: str):
    r = interpolar(registros, t, ["temperatura_c"])
    if r is None:
        return None
    v, ta, tb, peso = r
    temp = round(v["temperatura_c"], 3)
    if not -60.0 <= temp <= 60.0:
        return None
    fecha = t.isoformat().replace("+00:00", "Z")
    return {"evento_id": _id("i2t", ubicacion, fecha, temp), "fecha_evento": fecha, "ubicacion": ubicacion,
            "temperatura_c": temp, "origen": ORIGEN, "modo_publicacion": MODO,
            "ancla_hora_a": ta.isoformat().replace("+00:00", "Z"), "ancla_hora_b": tb.isoformat().replace("+00:00", "Z"),
            "peso_interpolacion": round(peso, 4)}
