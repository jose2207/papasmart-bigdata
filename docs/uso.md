# Uso del sistema

| Paso | Qué hacer | Dónde |
|---|---|---|
| 1 | Levantar la base (Kafka, PostgreSQL, Jupyter, tópicos) | [Instalación](instalacion.md) |
| 2 | **DimensiónU1** de cada integrante: ejecutar el cuaderno batch de arriba a abajo | Jupyter `http://localhost:4489/lab` |
| 3 | **DimensiónU2**: carga inicial + entrenamiento (Pasos 0–3 del cuaderno U2) | Jupyter |
| 4 | Arrancar consumers Spark y productores (flujo cada 2 min) | `iniciar_streaming*.bat`, `iniciar_tiempo_real_2min.bat` |
| 5 | Ver los datos llegar y las predicciones | Grafana `http://localhost:3300` (filas 01–08), Kafka UI `:48086` |
| 6 | **Ejecución integrada** con compuertas y manifiesto | Cuaderno `U3_Integracion_DataOps_S13_S14.ipynb` |
| 7 | Auditoría de configuración y pruebas | `python scripts/auditoria_config.py` · `python -m unittest discover -s pruebas -v` |

Casos de uso: el técnico agrícola consulta el tablero y ve la **humedad del suelo** y la **temperatura** actuales, su predicción a corto plazo y las alertas didácticas (humedad baja, helada).
