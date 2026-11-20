#!/usr/bin/env bash
set -euo pipefail
cd /home/jovyan/work/Sensortemperatura
mkdir -p .spark-ivy checkpoints
exec spark-submit \
  --master local[2] \
  --conf spark.jars.ivy=/home/jovyan/work/Sensortemperatura/.spark-ivy \
  --conf spark.sql.session.timeZone=UTC \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  /opt/agrosmart-scripts/consumer_streaming_temperatura.py
