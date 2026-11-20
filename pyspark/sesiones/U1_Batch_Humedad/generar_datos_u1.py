"""Genera el Excel de la Unidad 1 (batch) SOLO con humedad.

Base REAL: histórico Open-Meteo (humedad del suelo 0-1 cm y del aire 2 m, Puno).
Para practicar calidad de datos (S3) se INYECTAN fallas controladas y reproducibles:
  * código de error de sensor -999 en el suelo (no es un nulo),
  * nulos sueltos,
  * marcas de tiempo duplicadas en la fuente del aire.
La tercera fuente (suelo 1-3 cm) es SIMULADA a partir del suelo 0-1 cm (suavizado + ruido).
Uso:  python generar_datos_u1.py <historico_open_meteo.csv>
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
CSV_HIST = Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI.parent / "Sensorhumedad" / "datos" / "historico_open_meteo.csv"
DATA = AQUI / "data"
DATA.mkdir(exist_ok=True)

rng = np.random.default_rng(2026)
h = pd.read_csv(CSV_HIST, parse_dates=["fecha_evento"]).sort_values("fecha_evento").reset_index(drop=True)
h["fecha_hora"] = h.fecha_evento.dt.tz_convert("UTC").dt.strftime("%Y-%m-%d %H:%M:%S")

# --- Fuente A: suelo 0-1 cm (real + fallas inyectadas)
a = h[["fecha_hora", "humedad_suelo_pct"]].copy()
idx = rng.choice(len(a), 40, replace=False)
a.loc[idx[:25], "humedad_suelo_pct"] = -999.0          # código de error de sensor
a.loc[idx[25:], "humedad_suelo_pct"] = np.nan          # nulos
# --- Fuente B: aire 2 m (real + nulos + duplicados)
b = h[["fecha_hora", "humedad_aire_pct"]].copy()
b.loc[rng.choice(len(b), 8, replace=False), "humedad_aire_pct"] = np.nan
dup = b.iloc[rng.choice(len(b), 30, replace=False)].copy()
dup["humedad_aire_pct"] = np.where(rng.random(len(dup)) < 0.5, np.nan, dup["humedad_aire_pct"])
b = pd.concat([b, dup]).sort_values("fecha_hora", kind="stable").reset_index(drop=True)
# --- Fuente C: suelo 1-3 cm SIMULADO
s = h.humedad_suelo_pct.ewm(span=6, adjust=False).mean() * 0.97 + rng.normal(0, 0.15, len(h))
c = pd.DataFrame({"fecha_hora": h.fecha_hora, "humedad_suelo_1_3cm_pct": s.round(2)})

dic = pd.DataFrame([
    ["suelo_0_1cm", "fecha_hora", "UTC, cada hora", "Clave de integración"],
    ["suelo_0_1cm", "humedad_suelo_pct", "% volumétrico", "OBJETIVO. -999 = código de error de sensor; vacío = nulo. Open-Meteo (modelado) con fallas inyectadas"],
    ["aire_2m", "fecha_hora", "UTC, cada hora", "Clave; puede venir DUPLICADA"],
    ["aire_2m", "humedad_aire_pct", "% relativa", "Open-Meteo (modelado) con nulos y duplicados inyectados"],
    ["suelo_1_3cm_sim", "fecha_hora", "UTC, cada hora", "Clave de integración"],
    ["suelo_1_3cm_sim", "humedad_suelo_1_3cm_pct", "% volumétrico", "SIMULADA a partir de la 0-1 cm; no es medición"],
], columns=["hoja", "columna", "unidad", "descripcion"])

xlsx = DATA / "AgroSmart_Humedad_U1.xlsx"
with pd.ExcelWriter(xlsx, engine="openpyxl") as w:
    a.to_excel(w, sheet_name="suelo_0_1cm", index=False)
    b.to_excel(w, sheet_name="aire_2m", index=False)
    c.to_excel(w, sheet_name="suelo_1_3cm_sim", index=False)
    dic.to_excel(w, sheet_name="diccionario", index=False)
# copias CSV (Spark lee CSV en S2/S3: el Excel es la fuente "de negocio")
a.to_csv(DATA / "suelo_0_1cm.csv", index=False)
b.to_csv(DATA / "aire_2m.csv", index=False)
c.to_csv(DATA / "suelo_1_3cm_sim.csv", index=False)
print("OK", xlsx, "| A:", len(a), "B:", len(b), "C:", len(c))
