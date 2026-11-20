"""Escenarios didácticos de costos en soles. NO tarifas publicadas ni cotización.
Uso: python costos_pen.py --tarifa-computo-hora 0.30 --tarifa-gb-mes 0.40
"""
from __future__ import annotations
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def costo_pen(eventos_hora, bytes_por_evento, horas_mes, tarifa_compute,
              tarifa_gb, retencion_meses=1, factor_almacen=3):
    if min(eventos_hora,bytes_por_evento,horas_mes,tarifa_compute,tarifa_gb,retencion_meses,factor_almacen)<0:
        raise ValueError("No se permiten valores negativos")
    eventos = eventos_hora * horas_mes
    gb_mes = eventos * bytes_por_evento * factor_almacen * retencion_meses / 1e9
    computo = horas_mes * tarifa_compute
    almacen = gb_mes * tarifa_gb
    return {"eventos_mes":eventos,"almacen_gb_estimado":gb_mes,
            "computo_pen":computo,"almacen_pen":almacen,
            "total_parcial_pen":computo+almacen}


def metricas_db():
    import psycopg2
    conn=psycopg2.connect(host=os.getenv("POSTGRES_HOST","postgres"),
      dbname=os.getenv("POSTGRES_DB","agrosmart_u2"),
      user=os.getenv("POSTGRES_USER","agrosmart"),
      password=os.environ["POSTGRES_PASSWORD"],connect_timeout=8)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*),COALESCE(AVG(pg_column_size(t)),0) FROM eventos_telemetria t")
            n_telem,avg_t=cur.fetchone()
            cur.execute("SELECT COUNT(*),COALESCE(AVG(pg_column_size(e)),0) FROM eventos_empresariales e")
            n_emp,avg_e=cur.fetchone()
            cur.execute("SELECT COUNT(*) FROM predicciones_humedad")
            n_pred=cur.fetchone()[0]
            cur.execute("SELECT MIN(ingestado_utc),MAX(ingestado_utc) FROM eventos_telemetria")
            ini,fin=cur.fetchone()
        tiempo_h=max((fin-ini).total_seconds()/3600,1.0) if ini and fin else None
        # NO calcular tasa de operación regular usando ráfagas históricas de replay.
        return {"telemetria":n_telem,"empresarial":n_emp,"predicciones":n_pred,
                "tamano_medio_fila_suelo_bytes":float(avg_t),"tamano_medio_fila_empresa_bytes":float(avg_e),
                "duracion_ingesta_horas":tiempo_h}
    finally: conn.close()


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--tarifa-computo-hora", type=float,default=0.30)
    p.add_argument("--tarifa-gb-mes", type=float,default=0.40)
    p.add_argument("--horas-mes", type=int,default=720)
    p.add_argument("--bytes-evento", type=int,default=500,help="respaldo si DB vacía")
    p.add_argument("--factor-almacen", type=float,default=3.0,
                   help="sobrecoste didáctico de índices/checkpoints/copias")
    p.add_argument("--salida", default="/home/jovyan/work/Sensorhumedad/resultados/costos_pen.json")
    args=p.parse_args()
    try:
        observado=metricas_db()
        promedio=(observado["tamano_medio_fila_suelo_bytes"]+observado["tamano_medio_fila_empresa_bytes"])
        bytes_estimados=max(int(promedio),1)
    except Exception as exc:
        observado={"error":"DB sin evidencia o inaccesible: "+str(exc)}
        bytes_estimados=args.bytes_evento
    resultados={
      "moneda":"PEN / soles (S/)","calidad":"ESCENARIOS HIPOTÉTICOS, NO FACTURA NI PRECIO VERIFICADO",
      "fecha_utc":datetime.now(timezone.utc).isoformat(),
      "tarifa_computo_hora_pen":args.tarifa_computo_hora,
      "tarifa_almacen_gb_mes_pen":args.tarifa_gb_mes,
      "horas_mes":args.horas_mes,"bytes_evento_estimados":bytes_estimados,
      "factor_almacen":args.factor_almacen,"mediciones_db":observado,
      "escenarios":{
         f"{n}_eventos_hora":costo_pen(n,bytes_estimados,args.horas_mes,
           args.tarifa_computo_hora,args.tarifa_gb_mes,factor_almacen=args.factor_almacen)
         for n in [1,24,240]
      },
      "exclusiones":"API comercial, Internet/red, backups reales, infraestructura HA, salarios, electricidad, soporte e impuestos"
    }
    destino=Path(args.salida);destino.parent.mkdir(parents=True,exist_ok=True)
    destino.write_text(json.dumps(resultados,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Costos parciales estimados en SOLES (S/); NO son tarifas de un proveedor")
    for nombre,r in resultados["escenarios"].items():
        print(f"{nombre}: S/ {r['total_parcial_pen']:.2f} / mes, {r['almacen_gb_estimado']:.6f} GB aprox.")
    try:
        import psycopg2
        with psycopg2.connect(host=os.getenv("POSTGRES_HOST","postgres"),
              dbname=os.getenv("POSTGRES_DB","agrosmart_u2"),
              user=os.getenv("POSTGRES_USER","agrosmart"),
              password=os.environ["POSTGRES_PASSWORD"],connect_timeout=8) as conn:
            with conn.cursor() as cur:
                for n in (1,24,240):
                    r=resultados["escenarios"][f"{n}_eventos_hora"]
                    cur.execute("""INSERT INTO escenarios_costos
                      (nombre,eventos_hora,eventos_mes,almacenamiento_gb,computo_pen,almacenamiento_pen,total_pen)
                      VALUES (%s,%s,%s,%s,%s,%s,%s)
                      ON CONFLICT(nombre) DO UPDATE SET
                      eventos_hora=EXCLUDED.eventos_hora,eventos_mes=EXCLUDED.eventos_mes,
                      almacenamiento_gb=EXCLUDED.almacenamiento_gb,
                      computo_pen=EXCLUDED.computo_pen,almacenamiento_pen=EXCLUDED.almacenamiento_pen,
                      total_pen=EXCLUDED.total_pen,fecha_calculo=NOW()""",
                      (f"{n} eventos/h",n,int(r["eventos_mes"]),r["almacen_gb_estimado"],
                       r["computo_pen"],r["almacen_pen"],r["total_parcial_pen"]))
        print("Escenarios S/ guardados también en PostgreSQL para Grafana")
    except Exception as exc:
        print("No se pudieron registrar escenarios en DB; se conserva el JSON:",exc)
    print("Reporte:",destino)


if __name__ == "__main__": main()
