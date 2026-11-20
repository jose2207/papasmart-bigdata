#!/bin/bash
# Ejecuta cuadernos dentro del contenedor Jupyter (con pyspark en el PYTHONPATH) y deja un resumen.
export PYTHONPATH="/usr/local/spark/python:$(ls /usr/local/spark/python/lib/py4j-*.zip | head -1):${PYTHONPATH}"
cd /home/jovyan/work
RES=/home/jovyan/work/resumen_ejecucion.txt
for nb in "$@"; do
  ini=$(date +%s)
  echo ">>> Ejecutando $nb ..."
  if jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=3600 "$nb" > /tmp/nb.log 2>&1; then
    echo "OK     $(( $(date +%s) - ini )) s  $nb" | tee -a "$RES"
  else
    echo "FALLO  $(( $(date +%s) - ini )) s  $nb" | tee -a "$RES"
    tail -40 /tmp/nb.log | tee -a "$RES"
  fi
done
