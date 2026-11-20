"""Pruebas de NO REGRESIÓN de la configuración (S14): se repiten después de cada cambio.
Ejecutar: python -m unittest discover -s pruebas -v
"""
import json, re, sys, unittest
from pathlib import Path
import yaml

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "scripts"))
from auditoria_config import auditar  # noqa: E402


class ListaDeComprobacionTests(unittest.TestCase):
    def test_ningun_punto_falla(self):
        fallas = [f for f in auditar() if f["resultado"] == "Falla"]
        self.assertEqual(fallas, [], f"Puntos de la lista de comprobación que fallan: {fallas}")

    def test_riesgos_aceptados_tienen_justificacion(self):
        for f in (x for x in auditar() if x["resultado"] == "Aceptado"):
            self.assertGreater(len(f["detalle"]), 25, f"Riesgo aceptado sin justificación: {f['punto']}")


class IntegridadDelSistemaTests(unittest.TestCase):
    def test_esquemas_sql_crean_las_tablas_esperadas(self):
        sql = "".join((BASE / "pyspark" / "sql" / f).read_text(encoding="utf-8") for f in ("schema.sql", "schema_temperatura.sql", "schema_integracion.sql"))
        for tabla in ("eventos_telemetria", "predicciones_humedad", "ventanas_humedad", "metricas_modelo", "metricas_pipeline",
                      "eventos_temperatura", "predicciones_temperatura", "ventanas_temperatura", "metricas_modelo_temperatura", "ejecuciones_integracion"):
            self.assertRegex(sql, rf"CREATE TABLE IF NOT EXISTS {tabla}\b", tabla)

    def test_dashboard_unico_con_paneles_de_ambos_integrantes(self):
        d = json.loads((BASE / "obs/grafana/dashboards/agrosmart_u2.json").read_text(encoding="utf-8"))
        ids = [p["id"] for p in d["panels"]]
        self.assertEqual(len(ids), len(set(ids)), "ids de panel repetidos")
        titulos = " ".join(p.get("title", "") for p in d["panels"])
        self.assertIn("MIJAEL", titulos)
        self.assertGreaterEqual(len(ids), 40)
        uids = set(re.findall(r'"uid": "(agrosmart_[a-z]+)"', json.dumps(d)))
        self.assertLessEqual(uids, {"agrosmart_pg", "agrosmart_prom"})

    def test_artefactos_de_ambas_dimensiones_existen(self):
        for ruta in ("pyspark/sesiones/U1_Batch_Humedad/U1_AgroSmart_S01_S05_Humedad_Batch.ipynb",
                     "pyspark/sesiones/U1_Batch_Temperatura/U1_Mijael_Temperatura_S01_S05_Batch.ipynb",
                     "pyspark/sesiones/Sensorhumedad/U2_AgroSmart_S06_S12_Humedad_Tiempo_Real.ipynb",
                     "pyspark/sesiones/Sensortemperatura/U2_Mijael_Temperatura_S06_S12_Tiempo_Real.ipynb",
                     "pyspark/sesiones/U3_Integracion/U3_Integracion_DataOps_S13_S14.ipynb",
                     "pyspark/scripts/consumer_streaming.py", "pyspark/scripts/consumer_streaming_temperatura.py",
                     "uso-agrosmart/producer/producer_api_2min.py", "GUIA_EJECUCION_CMD.md"):
            self.assertTrue((BASE / ruta).exists(), ruta)

    def test_cuadernos_tienen_sintaxis_valida(self):
        import ast
        for nb in BASE.glob("pyspark/sesiones/**/*.ipynb"):
            for i, c in enumerate(json.loads(nb.read_text(encoding="utf-8"))["cells"]):
                if c["cell_type"] == "code":
                    src = re.sub(r"^\s*[!%].*$", "pass", "".join(c["source"]), flags=re.M)
                    ast.parse(src)

    def test_nav_de_mkdocs_apunta_a_paginas_existentes(self):
        # mkdocs.yml usa la etiqueta !!python/name (diagramas mermaid): se ignora al leer solo el nav
        class _Cargador(yaml.SafeLoader):
            pass
        _Cargador.add_multi_constructor("tag:yaml.org,2002:python/", lambda carg, sufijo, nodo: None)
        m = yaml.load((BASE / "mkdocs.yml").read_text(encoding="utf-8"), Loader=_Cargador)
        archivos = []
        def rec(n):
            for it in n:
                for _, v in it.items():
                    rec(v) if isinstance(v, list) else archivos.append(v)
        rec(m["nav"])
        faltan = [a for a in archivos if not (BASE / "docs" / a).exists()]
        self.assertEqual(faltan, [])


if __name__ == "__main__":
    unittest.main()
