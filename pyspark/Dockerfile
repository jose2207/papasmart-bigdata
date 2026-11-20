FROM jupyter/pyspark-notebook:spark-3.5.0
USER root
RUN python -m pip install --no-cache-dir \
    requests==2.32.3 pandas numpy matplotlib \
    kafka-python==2.0.2 psycopg2-binary==2.9.10 \
    prometheus-client==0.21.1 mkdocs==1.6.1 mkdocs-material==9.6.5 openpyxl
USER ${NB_UID}
