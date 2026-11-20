# S10 · Modelado de series de tiempo

**José · DimensiónU2.** Esta sesión aporta al monitoreo y predicción en tiempo real de la humedad.

Notebook: `pyspark/sesiones/Sensorhumedad/01_entrenamiento_y_verificacion_humedad.ipynb`.

- Serie principal: humedad volumétrica del suelo (%), secundaria: humedad relativa del aire (%).
- Predicción a +1, +2 y +3 h con variables disponibles al tiempo de emisión (suelo, aire y seno/coseno de la hora).
- Train 70 %, validación 15 %, prueba 15 %, separación cronológica y brecha de `h` filas para evitar que etiquetas crucen el corte.
- Modelos MLlib: Regresión Lineal, Random Forest, Árbol de Decisión, GBT. Baseline: persistencia.
- Selección por RMSE de **validación**, nunca usando el error del conjunto de prueba. Se registran RMSE, MAE y R² de prueba y las filas utilizadas.
- Guardar artefactos `modelos/humedad_1h`, `2h`, `3h`. `consumer_streaming.py` los carga y usa `.transform()` por microlote.

**Precaución:** una serie modelada casi constante puede favorecer persistencia o un modelo simple; no alterar datos para obtener una curva. `es_retro=TRUE` distingue inferencias sobre replay histórico de pronósticos producidos antes de su hora objetivo.

**Datos de entrenamiento:** simulado (carga inicial) + histórico API; la **prueba es el último 15 % (API real)**. Se compara contra persistencia y se reporta el resultado tal como salga. Ver [pregunta general](../proyecto-sello/pregunta-general.md) (Dimensión 2).
