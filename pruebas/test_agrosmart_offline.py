"""Pruebas offline: sin Spark, Kafka ni conexión real a Open-Meteo.
Ejecutar desde la raíz con: python -m unittest discover -s pruebas -v
"""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
PRODUCER=BASE/'uso-agrosmart'/'producer'
SCRIPTS=BASE/'pyspark'/'scripts'
sys.path.insert(0,str(PRODUCER))
sys.path.insert(0,str(SCRIPTS))
from open_meteo_humedad import normalizar,fecha_utc
from decisiones import crear_evaluacion
from costos_pen import costo_pen

RESPUESTA={
  'hourly':{
   'time':['2026-10-01T00:00','2026-10-01T01:00','2026-10-01T02:00'],
   'soil_moisture_0_to_1cm':[.12,.121,None],
   'relative_humidity_2m':[65,66,67]
  }
}

class TestAPIModeled(unittest.TestCase):
    def test_conversion_unidades(self):
        registros=normalizar(RESPUESTA)
        self.assertEqual(len(registros),2)
        self.assertEqual(registros[0]['humedad_suelo_pct'],12.0)
        self.assertEqual(registros[0]['humedad_suelo_m3m3'],.12)
        self.assertEqual(registros[0]['humedad_aire_pct'],65)
        self.assertEqual(registros[0]['profundidad_suelo_cm'],'0-1')
    def test_idempotencia_eventos(self):
        a=normalizar(RESPUESTA)
        b=normalizar(RESPUESTA)
        self.assertEqual([x['evento_id'] for x in a],[x['evento_id'] for x in b])
    def test_humedad_invalida_se_descarta(self):
        r={'hourly':{'time':['2026-10-01T00:00'],
             'soil_moisture_0_to_1cm':[1.1],'relative_humidity_2m':[60]}}
        self.assertEqual(normalizar(r),[])
    def test_utc(self):
        self.assertEqual(fecha_utc('2026-10-01T00:00'),'2026-10-01T00:00:00Z')

class TestBusiness(unittest.TestCase):
    def test_unicamente_humedad(self):
        e=normalizar(RESPUESTA)[0]
        v=crear_evaluacion(e,20)
        self.assertEqual(v['tipo'],'evaluacion_humedad')
        self.assertEqual(v['estado'],'revision_manual')
        self.assertNotIn('volumen_litros',v)
        self.assertNotIn('ventas',v)
        self.assertEqual(v['evento_telemetria_id'],e['evento_id'])
        self.assertEqual(crear_evaluacion(e,20)['evento_id'],v['evento_id'])
    def test_umbral_docente_no_agronomico(self):
        e=normalizar(RESPUESTA)[1]
        self.assertEqual(crear_evaluacion(e,10)['estado'],'seguimiento')

class TestCosting(unittest.TestCase):
    def test_soles_costo_parcial(self):
        c=costo_pen(24,500,720,.30,.40,factor_almacen=3)
        self.assertEqual(c['eventos_mes'],17280)
        self.assertAlmostEqual(c['computo_pen'],216.0)
        self.assertGreater(c['total_parcial_pen'],216)
    def test_no_negativos(self):
        with self.assertRaises(ValueError):
            costo_pen(-1,500,720,.3,.4)

class TestProjectStructure(unittest.TestCase):
    def test_files_exist(self):
        files=['kafka/compose.yml','pyspark/compose.yml','pyspark/compose.kafka.yml',
           'pyspark/scripts/consumer_streaming.py','obs/compose.yml',
           'obs/grafana/dashboards/agrosmart_u2.json','mkdocs.yml',
           'uso-agrosmart/producer/producer_api_humedad.py',
           'uso-agrosmart/producer/producer_evaluaciones.py',
           'uso-agrosmart/consumer/consumer_verificacion.py']
        for f in files:
            with self.subTest(f=f):self.assertTrue((BASE/f).is_file())
    def test_dashboard_integracion(self):
        dash=json.loads((BASE/'obs/grafana/dashboards/agrosmart_u2.json').read_text())
        self.assertGreaterEqual(len(dash['panels']),18)
        sql=' '.join(t.get('rawSql','') for p in dash['panels'] for t in p.get('targets',[]))
        self.assertIn('predicciones_humedad',sql)
        self.assertIn('eventos_empresariales',sql)
        self.assertIn('eventos_telemetria',sql)
        self.assertIn('escenarios_costos',sql)
        self.assertNotIn('volumen_litros',sql)

if __name__=='__main__':unittest.main()


class SimuladorHumedadTests(unittest.TestCase):
    def setUp(self):
        import sys
        sys.path.insert(0, str(BASE / 'uso-agrosmart' / 'producer'))
        from simulador_humedad import simular
        from datetime import datetime, timezone
        self.simular = simular
        self.fin = datetime(2026, 9, 7, 20, tzinfo=timezone.utc)

    def test_cantidad_y_continuidad_horaria(self):
        f = self.simular(self.fin, dias=10)
        self.assertEqual(len(f), 240)
        from datetime import datetime, timedelta
        t = [datetime.fromisoformat(x['fecha_evento'].replace('Z', '+00:00')) for x in f]
        self.assertTrue(all(b - a == timedelta(hours=1) for a, b in zip(t, t[1:])))
        self.assertEqual(t[-1] + timedelta(hours=1), self.fin)

    def test_rangos_validos_y_ids_unicos(self):
        f = self.simular(self.fin, dias=30)
        self.assertTrue(all(0 <= x['humedad_suelo_pct'] <= 100 and 0 <= x['humedad_aire_pct'] <= 100 for x in f))
        self.assertTrue(all(abs(x['humedad_suelo_m3m3'] * 100 - x['humedad_suelo_pct']) < 1e-3 for x in f))
        self.assertEqual(len({x['evento_id'] for x in f}), len(f))
        self.assertTrue(all(x['origen'] == 'simulado_carga_inicial' for x in f))

    def test_reproducible(self):
        self.assertEqual(self.simular(self.fin, dias=5), self.simular(self.fin, dias=5))


class TemperaturaMijaelTests(unittest.TestCase):
    def setUp(self):
        import sys
        sys.path.insert(0, str(BASE / 'uso-agrosmart' / 'producer'))
        from datetime import datetime, timezone
        self.fin = datetime(2026, 9, 7, 20, tzinfo=timezone.utc)

    def test_simulador_continuidad_rango_y_reproducible(self):
        from simulador_temperatura import simular
        from datetime import datetime, timedelta
        f = simular(self.fin, dias=20)
        self.assertEqual(len(f), 480)
        t = [datetime.fromisoformat(x['fecha_evento'].replace('Z', '+00:00')) for x in f]
        self.assertTrue(all(b - a == timedelta(hours=1) for a, b in zip(t, t[1:])))
        self.assertEqual(t[-1] + timedelta(hours=1), self.fin)
        self.assertTrue(all(-15 <= x['temperatura_c'] <= 30 for x in f))
        self.assertEqual(len({x['evento_id'] for x in f}), len(f))
        self.assertEqual(f, simular(self.fin, dias=20))

    def test_simulador_ciclo_diario(self):
        from simulador_temperatura import simular
        from datetime import datetime
        f = simular(self.fin, dias=40)
        por_hora = {}
        for x in f:
            h = datetime.fromisoformat(x['fecha_evento'].replace('Z', '+00:00')).hour
            por_hora.setdefault(h, []).append(x['temperatura_c'])
        medias = {h: sum(v) / len(v) for h, v in por_hora.items()}
        self.assertGreater(medias[19], medias[10] + 6)   # tarde local (14 h) mucho más cálida que el amanecer (5 h)

    def test_normalizar_api_temperatura(self):
        from open_meteo_temperatura import normalizar
        r = {'hourly': {'time': ['2026-11-05T14:00', '2026-11-05T15:00', '2026-11-05T16:00'],
                        'temperature_2m': [12.5, None, 99.0]}}
        s = normalizar(r)
        self.assertEqual(len(s), 1)
        self.assertEqual(s[0]['temperatura_c'], 12.5)
        self.assertEqual(s[0]['fecha_evento'], '2026-11-05T14:00:00Z')
        with self.assertRaises(ValueError):
            normalizar({'hourly': {'time': []}})

    def test_evaluacion_helada(self):
        from decisiones_temperatura import crear_evaluacion
        base = {'evento_id': 'x', 'fecha_evento': '2026-11-05T10:00:00Z', 'ubicacion': 'Azángaro'}
        self.assertEqual(crear_evaluacion({**base, 'temperatura_c': -2.0})['estado'], 'alerta_helada')
        self.assertEqual(crear_evaluacion({**base, 'temperatura_c': 2.0})['estado'], 'vigilancia')
        self.assertEqual(crear_evaluacion({**base, 'temperatura_c': 9.0})['estado'], 'normal')
        with self.assertRaises(ValueError):
            crear_evaluacion({**base, 'temperatura_c': 99.0})


class Flujo2MinTests(unittest.TestCase):
    def setUp(self):
        import sys
        sys.path.insert(0, str(BASE / 'uso-agrosmart' / 'producer'))

    def _horas(self, campo_base):
        return [dict(fecha_evento=f'2026-11-14T{h:02d}:00:00Z', **campo_base(h)) for h in range(10, 14)]

    def test_instante_2min_y_interpolacion_lineal(self):
        from interpolacion_2min import instante_2min, interpolar, a_utc
        from datetime import datetime, timezone
        self.assertEqual(instante_2min(datetime(2026, 11, 14, 11, 37, 55, tzinfo=timezone.utc)).minute, 36)
        reg = self._horas(lambda h: {'temperatura_c': float(h)})          # 10,11,12,13
        v, ta, tb, peso = interpolar(reg, a_utc('2026-11-14T11:30:00Z'), ['temperatura_c'])
        self.assertAlmostEqual(v['temperatura_c'], 11.5, places=6)
        self.assertAlmostEqual(peso, 0.5, places=6)
        v, *_ = interpolar(reg, a_utc('2026-11-14T12:00:00Z'), ['temperatura_c'])   # justo en la hora
        self.assertAlmostEqual(v['temperatura_c'], 12.0, places=6)
        self.assertIsNone(interpolar(reg, a_utc('2026-11-14T13:30:00Z'), ['temperatura_c']))   # sin ancla posterior
        self.assertIsNone(interpolar(reg, a_utc('2026-11-14T09:00:00Z'), ['temperatura_c']))   # sin ancla previa

    def test_no_interpola_a_traves_de_huecos(self):
        from interpolacion_2min import interpolar, a_utc
        reg = [{'fecha_evento': '2026-11-14T10:00:00Z', 'temperatura_c': 1.0}, {'fecha_evento': '2026-11-14T13:00:00Z', 'temperatura_c': 4.0}]
        self.assertIsNone(interpolar(reg, a_utc('2026-11-14T11:00:00Z'), ['temperatura_c']))

    def test_eventos_validos_para_el_consumer(self):
        from interpolacion_2min import evento_humedad, evento_temperatura, a_utc
        t = a_utc('2026-11-14T11:20:00Z')
        h = evento_humedad(self._horas(lambda x: {'humedad_suelo_pct': 10.0 + x, 'humedad_aire_pct': 40.0}), t, 'Puno')
        self.assertTrue(0 <= h['humedad_suelo_m3m3'] <= 1 and h['origen'] == 'open_meteo_interpolado_2min' and h['modo_publicacion'] == 'interpolado_2min')
        self.assertAlmostEqual(h['humedad_suelo_pct'], 21.3333, places=3)
        tt = evento_temperatura(self._horas(lambda x: {'temperatura_c': float(x)}), t, 'Azángaro')
        self.assertAlmostEqual(tt['temperatura_c'], 11.333, places=3)
        for k in ('evento_id', 'fecha_evento', 'ubicacion', 'origen'):
            self.assertTrue(tt[k] and h[k])
        # determinista: mismo instante => mismo id (idempotencia)
        self.assertEqual(tt['evento_id'], evento_temperatura(self._horas(lambda x: {'temperatura_c': float(x)}), t, 'Azángaro')['evento_id'])
