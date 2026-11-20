"""Genera el Excel de la DIMENSIÓN U1 de Mijael (temperatura exterior, Azángaro) — datos SIMULADOS y reproducibles.
Base: simulador_temperatura.py (120 días horarios, hasta 2026-11-11 00:00 UTC), calibrado al clima del altiplano.
Se INYECTAN fallas para practicar calidad de datos (S3):
  * hoja temperatura_2m  : código de error -999 y nulos;
  * hoja temperatura_respaldo: segunda fuente (sensor de respaldo, sesgo +0.4 °C y ruido) con nulos y DUPLICADOS.
Uso: python generar_datos_u1_temperatura.py
"""
import sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[2] / "uso-agrosmart" / "producer"))
from simulador_temperatura import simular  # noqa: E402

DATA = AQUI / "data"; DATA.mkdir(exist_ok=True)
rng = np.random.default_rng(2026)
base = pd.DataFrame(simular(datetime(2026, 11, 11, tzinfo=timezone.utc), dias=120, semilla=11))
base["fecha_hora"] = pd.to_datetime(base.fecha_evento).dt.strftime("%Y-%m-%d %H:%M:%S")

a = base[["fecha_hora", "temperatura_c"]].copy()
idx = rng.choice(len(a), 45, replace=False)
a.loc[idx[:30], "temperatura_c"] = -999.0
a.loc[idx[30:], "temperatura_c"] = np.nan

b = pd.DataFrame({"fecha_hora": base.fecha_hora,
                  "temperatura_respaldo_c": (base.temperatura_c + 0.4 + rng.normal(0, 0.5, len(base))).round(1)})
b.loc[rng.choice(len(b), 10, replace=False), "temperatura_respaldo_c"] = np.nan
dup = b.iloc[rng.choice(len(b), 25, replace=False)].copy()
dup["temperatura_respaldo_c"] = np.where(rng.random(len(dup)) < 0.5, np.nan, dup["temperatura_respaldo_c"])
b = pd.concat([b, dup]).sort_values("fecha_hora", kind="stable").reset_index(drop=True)

dic = pd.DataFrame([
 ["temperatura_2m", "fecha_hora", "UTC, cada hora", "Clave de integración"],
 ["temperatura_2m", "temperatura_c", "°C", "OBJETIVO. -999 = error de sensor; vacío = nulo. SIMULADA (altiplano de Azángaro)"],
 ["temperatura_respaldo", "fecha_hora", "UTC, cada hora", "Clave; puede venir DUPLICADA"],
 ["temperatura_respaldo", "temperatura_respaldo_c", "°C", "Sensor de respaldo SIMULADO (sesgo +0.4 °C); sirve para rellenar huecos de la fuente principal"],
], columns=["hoja", "columna", "unidad", "descripcion"])

xlsx = DATA / "AgroSmart_Temperatura_U1.xlsx"
with pd.ExcelWriter(xlsx, engine="openpyxl") as w:
    a.to_excel(w, sheet_name="temperatura_2m", index=False)
    b.to_excel(w, sheet_name="temperatura_respaldo", index=False)
    dic.to_excel(w, sheet_name="diccionario", index=False)
a.to_csv(DATA / "temperatura_2m.csv", index=False)
b.to_csv(DATA / "temperatura_respaldo.csv", index=False)
print("OK", xlsx, "| A:", len(a), "B:", len(b))
