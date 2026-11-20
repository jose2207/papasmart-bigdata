#!/usr/bin/env python3
"""Lista de comprobación de configuración (S14, Tabla 2) aplicada a los archivos de Docker Compose del proyecto.
Puntos: versión de imágenes · reinicio · salud · orden de arranque · secretos · superficie expuesta · variables del .env.
Uso: python scripts/auditoria_config.py [--json salida.json]   (código de salida 1 si algún punto FALLA)
"""
from __future__ import annotations
import json, re, sys
from datetime import datetime, timezone
from pathlib import Path
import yaml

BASE = Path(__file__).resolve().parents[1]
COMPOSES = ["kafka/compose.yml", "pyspark/compose.yml", "pyspark/compose.kafka.yml", "obs/compose.yml", "uso-agrosmart/compose.yml"]

# Servicios permanentes que DEBEN declarar healthcheck
CON_SALUD = {"kafka", "postgres", "jupyter", "exporter", "prometheus", "pushgateway", "grafana", "spark-consumer", "spark-consumer-temperatura"}
# Riesgos ACEPTADOS (S14, 2.6): sin healthcheck por una razón explícita
ACEPTADOS = {
    "kafka-ui": "Interfaz de apoyo; la imagen no garantiza utilidades de shell. Si cae, no afecta al flujo de datos.",
    "kafka-exporter": "Imagen mínima sin shell; su estado se observa desde Prometheus (target kafka_exporter UP/DOWN).",
}
SECRETO = re.compile(r"(PASSWORD|TOKEN|SECRET|API_KEY)", re.I)


def cargar():
    docs = {}
    for f in COMPOSES:
        ruta = BASE / f
        if ruta.exists():
            docs[f] = yaml.safe_load(ruta.read_text(encoding="utf-8")) or {}
    return docs


def servicios(docs):
    for f, d in docs.items():
        for nombre, s in (d.get("services") or {}).items():
            yield f, nombre, s or {}


def auditar() -> list[dict]:
    docs, filas = cargar(), []
    add = lambda punto, ok, detalle, estado=None: filas.append({"punto": punto, "resultado": estado or ("Cumple" if ok else "Falla"), "detalle": detalle})
    sin_version = [f"{f}:{n}" for f, n, s in servicios(docs) if s.get("image") and (":" not in s["image"] or s["image"].endswith(":latest"))]
    add("Versión de las imágenes", not sin_version, "Todas las imágenes tienen versión exacta." if not sin_version else f"Sin versión exacta: {sin_version}")
    # un servicio puede redefinirse en varios archivos (p. ej. jupyter en compose.yml y compose.kafka.yml): se evalúa la unión
    con_restart = {n for f, n, s in servicios(docs) if "restart" in s}
    sin_restart = sorted({n for f, n, s in servicios(docs) if (s.get("image") or s.get("build")) and n not in con_restart and not f.startswith("uso-agrosmart/")})
    add("Reinicio (restart)", not sin_restart, "Los servicios permanentes declaran restart." if not sin_restart else f"Sin restart: {sin_restart}")
    con_salud = {n for f, n, s in servicios(docs) if "healthcheck" in s}
    definidos = {n for f, n, s in servicios(docs)}
    faltan = sorted((CON_SALUD & definidos) - con_salud)
    add("Salud (healthcheck)", not faltan, f"Healthcheck en {len(CON_SALUD)} servicios permanentes." if not faltan else f"Sin healthcheck: {faltan}")
    for n, motivo in ACEPTADOS.items():
        add(f"Salud · riesgo aceptado: {n}", True, motivo, estado="Aceptado")
    con_hc = {(f, n) for f, n, s in servicios(docs) if "healthcheck" in s}
    nombres_hc = {n for _, n in con_hc}
    mal = []
    for f, n, s in servicios(docs):
        dep = s.get("depends_on") or {}
        items = dep.items() if isinstance(dep, dict) else [(d, {}) for d in dep]
        for d, cond in items:
            if d in nombres_hc and (cond or {}).get("condition") != "service_healthy":
                mal.append(f"{f}:{n}→{d}")
    add("Orden de arranque (depends_on)", not mal, "Toda dependencia con healthcheck espera a service_healthy." if not mal else f"Esperan solo a 'arrancó': {mal}")
    literales = []
    for f, n, s in servicios(docs):
        env = s.get("environment") or {}
        env = env if isinstance(env, dict) else dict(x.split("=", 1) for x in env if "=" in x)
        for k, v in env.items():
            if SECRETO.search(str(k)) and v not in (None, "") and not str(v).startswith("${"):
                literales.append(f"{f}:{n}:{k}")
    gi = (BASE / ".gitignore").read_text(encoding="utf-8") if (BASE / ".gitignore").exists() else ""
    add("Secretos fuera del archivo", not literales and ".env" in gi, "Credenciales por ${VARIABLE}; .env en .gitignore." if not literales and ".env" in gi else f"Literales: {literales}; .env ignorado: {'.env' in gi}")
    abiertos, publicados = [], []
    for f, n, s in servicios(docs):
        for p in s.get("ports") or []:
            publicados.append(f"{n}:{p}")
            if not str(p).startswith("127.0.0.1:"):
                abiertos.append(f"{f}:{n}:{p}")
    add("Superficie expuesta (ports)", not abiertos, f"{len(publicados)} puertos publicados, todos en 127.0.0.1 (solo el equipo local)." if not abiertos else f"Expuestos a toda la red: {abiertos}")
    usadas = set()
    for f in COMPOSES:
        txt = (BASE / f).read_text(encoding="utf-8")
        usadas |= set(re.findall(r"\$\{([A-Z_][A-Z0-9_]*)\}", txt))               # sin valor por defecto
    ejemplo = (BASE / ".env.example").read_text(encoding="utf-8") if (BASE / ".env.example").exists() else ""
    faltan_env = sorted(v for v in usadas if not re.search(rf"^{v}=", ejemplo, re.M))
    add("Variables documentadas en .env.example", not faltan_env, f"{len(usadas)} variables obligatorias, todas en .env.example." if not faltan_env else f"Faltan en .env.example: {faltan_env}")
    return filas


if __name__ == "__main__":
    filas = auditar()
    ancho = max(len(f["punto"]) for f in filas)
    for f in filas:
        print(f"[{f['resultado']:8s}] {f['punto']:{ancho}s}  {f['detalle']}")
    if "--json" in sys.argv:
        destino = Path(sys.argv[sys.argv.index("--json") + 1]); destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps({"generado_utc": datetime.now(timezone.utc).isoformat(), "resultados": filas}, indent=2, ensure_ascii=False), encoding="utf-8")
    sys.exit(1 if any(f["resultado"] == "Falla" for f in filas) else 0)
