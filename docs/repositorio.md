# Repositorio y estándares

```
AgroSmart_Puno_BigData_COMPLETO/
├─ docs/ · MkDocs (documentación publicada)           ├─ obs/ · Prometheus, exporter, Grafana (dashboard único)
├─ kafka/ · broker, Kafka UI, exporter                ├─ pruebas/ · unitarias y de no regresión
├─ pyspark/ · Jupyter, consumers, SQL, sesiones/      ├─ scripts/ · auditoría de configuración
├─ uso-agrosmart/ · productores, contratos, 2 min     └─ .github/workflows/ · CI y publicación de docs
```

## Estándares
- **Repositorio:** [https://github.com/jose2207/papasmart-bigdata](https://github.com/jose2207/papasmart-bigdata) · **MkDocs publicado:** [https://jose2207.github.io/papasmart-bigdata/](https://jose2207.github.io/papasmart-bigdata/)
- **Topics del repositorio:** `campus-juliaca`, `semestre-2026-2`, `linea-cdia`, `tipo-ps`, `bigdata`, `seccion-gu`, `grupo-11-agrosmart-puno`, `apache-kafka`, `spark-streaming`, `pyspark`, `grafana`, `prometheus`, `open-meteo`.
- **Una rama por sesión cerrada** y commits coherentes con las evidencias (las fechas de las capturas deben coincidir con el historial).
- **Sin secretos:** `.env` en `.gitignore`; `.env.example` solo con marcadores.
- **CI** (`.github/workflows/ci.yml`): pruebas, auditoría de configuración, validación de Compose y `mkdocs build --strict`.
- **Reproducibilidad:** `git status` limpio tras ejecutar el sistema; la guía de ejecución se sigue sin ayuda.
