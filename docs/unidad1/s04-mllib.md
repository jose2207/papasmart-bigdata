# S4 · ML distribuido con MLlib (regresión, CRISP‑DM)

**José · DimensiónU1.** Aporte de esta sesión: modelo base y comparación contra baseline.

- **Fases:** negocio → comprensión (correlaciones) → preparación (`VectorAssembler`, seno/coseno de la hora, split 80/20 con semilla) → modelado → evaluación → despliegue (guardar modelo).
- **Modelos:** baseline (promedio), lineal, Ridge, Elastic Net, Random Forest, GBT; métricas **RMSE, MAE, R²**.
- **Importancia de variables** (Random Forest).
- ⚠️ **Fuga por construcción:** `humedad_suelo_1_3cm_pct` es simulada desde el objetivo (corr ≈ 0.99). La **ablación** reentrena sin ella para ver el desempeño real.
- División **aleatoria** aquí; el pronóstico temporal con división **cronológica** es la Unidad 2 (S10).

**Evidencia:** sección 4 (tabla comparativa, gráfico, ablación, modelo en `artifacts/modelo_u1_humedad_suelo`).
