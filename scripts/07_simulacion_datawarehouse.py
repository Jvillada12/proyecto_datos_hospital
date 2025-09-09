#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PASO 7: SIMULACIÓN DE MIGRACIÓN A DATA WAREHOUSE
Simula la carga de datos limpios a estructura de Data Warehouse
"""

import pandas as pd
import json
import sqlite3
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DataWarehouseSimulator:
    """Simulador de migración a Data Warehouse"""
    
    def __init__(self):
        self.conn = None
        self.datos_limpios = None
        
    def conectar_dw(self):
        """Simula conexión a Data Warehouse (SQLite)"""
        self.conn = sqlite3.connect('../resultados/hospital_datawarehouse.db')
        print("Conexión a Data Warehouse establecida")
    
    def cargar_datos_limpios(self):
        """Carga datos limpios para migración"""
        with open('../resultados/dataset_hospital_limpio.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        self.datos_limpios = {
            'pacientes': pd.DataFrame(datos['pacientes']),
            'citas': pd.DataFrame(datos['citas_medicas'])
        }
        print("Datos limpios cargados para migración")
    
    def crear_esquema_dw(self):
        """Crea esquema de Data Warehouse"""
        
        # Tabla dimensional de pacientes
        sql_dim_pacientes = """
        CREATE TABLE IF NOT EXISTS dim_pacientes (
            sk_paciente INTEGER PRIMARY KEY,
            id_paciente_source INTEGER,
            nombre VARCHAR(100),
            fecha_nacimiento DATE,
            edad INTEGER,
            sexo CHAR(1),
            email VARCHAR(100),
            telefono VARCHAR(20),
            ciudad VARCHAR(50),
            fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT TRUE
        )
        """
        
        # Tabla dimensional de médicos
        sql_dim_medicos = """
        CREATE TABLE IF NOT EXISTS dim_medicos (
            sk_medico INTEGER PRIMARY KEY,
            nombre_medico VARCHAR(100),
            fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT TRUE
        )
        """
        
        # Tabla dimensional de especialidades
        sql_dim_especialidades = """
        CREATE TABLE IF NOT EXISTS dim_especialidades (
            sk_especialidad INTEGER PRIMARY KEY,
            nombre_especialidad VARCHAR(50),
            fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT TRUE
        )
        """
        
        # Tabla dimensional de tiempo
        sql_dim_tiempo = """
        CREATE TABLE IF NOT EXISTS dim_tiempo (
            sk_fecha INTEGER PRIMARY KEY,
            fecha DATE,
            año INTEGER,
            mes INTEGER,
            dia INTEGER,
            nombre_mes VARCHAR(20),
            trimestre INTEGER,
            dia_semana INTEGER,
            nombre_dia_semana VARCHAR(20),
            es_fin_semana BOOLEAN
        )
        """
        
        # Tabla de hechos de citas
        sql_fact_citas = """
        CREATE TABLE IF NOT EXISTS fact_citas_medicas (
            sk_cita INTEGER PRIMARY KEY,
            id_cita_source VARCHAR(50),
            sk_paciente INTEGER,
            sk_medico INTEGER,
            sk_especialidad INTEGER,
            sk_fecha_cita INTEGER,
            sk_fecha_carga INTEGER,
            costo DECIMAL(10,2),
            estado_cita VARCHAR(20),
            FOREIGN KEY (sk_paciente) REFERENCES dim_pacientes(sk_paciente),
            FOREIGN KEY (sk_medico) REFERENCES dim_medicos(sk_medico),
            FOREIGN KEY (sk_especialidad) REFERENCES dim_especialidades(sk_especialidad),
            FOREIGN KEY (sk_fecha_cita) REFERENCES dim_tiempo(sk_fecha)
        )
        """
        
        # Ejecutar creación de tablas
        cursor = self.conn.cursor()
        cursor.execute(sql_dim_pacientes)
        cursor.execute(sql_dim_medicos)
        cursor.execute(sql_dim_especialidades)
        cursor.execute(sql_dim_tiempo)
        cursor.execute(sql_fact_citas)
        self.conn.commit()
        
        print("Esquema de Data Warehouse creado exitosamente")
    
    def poblar_dimensiones(self):
        """Pobla las tablas dimensionales"""
        
        # Dimensión pacientes
        dim_pacientes = self.datos_limpios['pacientes'].copy()
        dim_pacientes['sk_paciente'] = range(1, len(dim_pacientes) + 1)
        dim_pacientes['id_paciente_source'] = dim_pacientes['id_paciente']
        dim_pacientes['activo'] = True
        
        dim_pacientes.to_sql('dim_pacientes', self.conn, if_exists='replace', index=False)
        print(f"Dimensión pacientes poblada: {len(dim_pacientes)} registros")
        
        # Dimensión médicos
        medicos_unicos = self.datos_limpios['citas']['medico'].dropna().unique()
        dim_medicos = pd.DataFrame({
            'sk_medico': range(1, len(medicos_unicos) + 1),
            'nombre_medico': medicos_unicos,
            'activo': True
        })
        
        dim_medicos.to_sql('dim_medicos', self.conn, if_exists='replace', index=False)
        print(f"Dimensión médicos poblada: {len(dim_medicos)} registros")
        
        # Dimensión especialidades
        especialidades_unicas = self.datos_limpios['citas']['especialidad'].dropna().unique()
        dim_especialidades = pd.DataFrame({
            'sk_especialidad': range(1, len(especialidades_unicas) + 1),
            'nombre_especialidad': especialidades_unicas,
            'activo': True
        })
        
        dim_especialidades.to_sql('dim_especialidades', self.conn, if_exists='replace', index=False)
        print(f"Dimensión especialidades poblada: {len(dim_especialidades)} registros")
        
        # Dimensión tiempo (fechas de los últimos 5 años)
        fechas = pd.date_range(start='2020-01-01', end='2030-12-31', freq='D')
        dim_tiempo = pd.DataFrame({
            'sk_fecha': range(1, len(fechas) + 1),
            'fecha': fechas,
            'año': fechas.year,
            'mes': fechas.month,
            'dia': fechas.day,
            'nombre_mes': fechas.strftime('%B'),
            'trimestre': fechas.quarter,
            'dia_semana': fechas.dayofweek,
            'nombre_dia_semana': fechas.strftime('%A'),
            'es_fin_semana': fechas.dayofweek >= 5
        })
        
        dim_tiempo.to_sql('dim_tiempo', self.conn, if_exists='replace', index=False)
        print(f"Dimensión tiempo poblada: {len(dim_tiempo)} registros")
    
    def poblar_hechos(self):
        """Pobla la tabla de hechos"""
        
        # Obtener mapeos de dimensiones
        dim_pacientes = pd.read_sql('SELECT sk_paciente, id_paciente_source FROM dim_pacientes', self.conn)
        dim_medicos = pd.read_sql('SELECT sk_medico, nombre_medico FROM dim_medicos', self.conn)
        dim_especialidades = pd.read_sql('SELECT sk_especialidad, nombre_especialidad FROM dim_especialidades', self.conn)
        dim_tiempo = pd.read_sql('SELECT sk_fecha, fecha FROM dim_tiempo', self.conn)
        
        # Preparar datos de hechos
        fact_citas = self.datos_limpios['citas'].copy()
        
        # Mapear a claves surrogadas
        fact_citas = fact_citas.merge(
            dim_pacientes.rename(columns={'id_paciente_source': 'id_paciente'}),
            on='id_paciente', how='left'
        )
        
        fact_citas = fact_citas.merge(
            dim_medicos.rename(columns={'nombre_medico': 'medico'}),
            on='medico', how='left'
        )
        
        fact_citas = fact_citas.merge(
            dim_especialidades.rename(columns={'nombre_especialidad': 'especialidad'}),
            on='especialidad', how='left'
        )
        
        # Mapear fechas
        dim_tiempo['fecha'] = pd.to_datetime(dim_tiempo['fecha']).dt.date
        fact_citas['fecha_cita'] = pd.to_datetime(fact_citas['fecha_cita']).dt.date
        
        fact_citas = fact_citas.merge(
            dim_tiempo.rename(columns={'fecha': 'fecha_cita', 'sk_fecha': 'sk_fecha_cita'}),
            on='fecha_cita', how='left'
        )
        
        # Fecha de carga (hoy)
        fecha_hoy = datetime.now().date()
        sk_fecha_hoy = dim_tiempo[dim_tiempo['fecha'] == fecha_hoy]['sk_fecha'].iloc[0] if len(dim_tiempo[dim_tiempo['fecha'] == fecha_hoy]) > 0 else 1
        
        # Seleccionar columnas finales
        fact_final = pd.DataFrame({
            'sk_cita': range(1, len(fact_citas) + 1),
            'id_cita_source': fact_citas['id_cita'],
            'sk_paciente': fact_citas['sk_paciente'],
            'sk_medico': fact_citas['sk_medico'],
            'sk_especialidad': fact_citas['sk_especialidad'],
            'sk_fecha_cita': fact_citas['sk_fecha_cita'],
            'sk_fecha_carga': sk_fecha_hoy,
            'costo': fact_citas['costo'],
            'estado_cita': fact_citas['estado_cita']
        })
        
        fact_final.to_sql('fact_citas_medicas', self.conn, if_exists='replace', index=False)
        print(f"Tabla de hechos poblada: {len(fact_final)} registros")
    
    def generar_reportes_dw(self):
        """Genera reportes de ejemplo desde el DW"""
        
        print("\nGENERANDO REPORTES DE EJEMPLO DESDE DATA WAREHOUSE")
        print("="*60)
        
        # Reporte 1: Citas por especialidad
        query1 = """
        SELECT 
            e.nombre_especialidad,
            COUNT(*) as total_citas,
            AVG(f.costo) as costo_promedio,
            SUM(f.costo) as ingresos_totales
        FROM fact_citas_medicas f
        JOIN dim_especialidades e ON f.sk_especialidad = e.sk_especialidad
        WHERE f.sk_especialidad IS NOT NULL
        GROUP BY e.nombre_especialidad
        ORDER BY total_citas DESC
        """
        
        reporte1 = pd.read_sql(query1, self.conn)
        print("\n1. ANÁLISIS POR ESPECIALIDAD:")
        print(reporte1.to_string(index=False))
        
        # Reporte 2: Productividad por médico
        query2 = """
        SELECT 
            m.nombre_medico,
            COUNT(*) as total_citas,
            COUNT(CASE WHEN f.estado_cita = 'Completada' THEN 1 END) as citas_completadas,
            ROUND(COUNT(CASE WHEN f.estado_cita = 'Completada' THEN 1 END) * 100.0 / COUNT(*), 2) as tasa_completamiento
        FROM fact_citas_medicas f
        JOIN dim_medicos m ON f.sk_medico = m.sk_medico
        WHERE f.sk_medico IS NOT NULL
        GROUP BY m.nombre_medico
        ORDER BY total_citas DESC
        LIMIT 10
        """
        
        reporte2 = pd.read_sql(query2, self.conn)
        print("\n2. PRODUCTIVIDAD POR MÉDICO:")
        print(reporte2.to_string(index=False))
        
        # Reporte 3: Análisis temporal
        query3 = """
        SELECT 
            t.año,
            t.trimestre,
            COUNT(*) as total_citas,
            AVG(f.costo) as costo_promedio
        FROM fact_citas_medicas f
        JOIN dim_tiempo t ON f.sk_fecha_cita = t.sk_fecha
        WHERE f.sk_fecha_cita IS NOT NULL
        GROUP BY t.año, t.trimestre
        ORDER BY t.año, t.trimestre
        """
        
        reporte3 = pd.read_sql(query3, self.conn)
        print("\n3. ANÁLISIS TEMPORAL:")
        print(reporte3.to_string(index=False))
        
        # Guardar reportes
        with open('../reportes/reportes_datawarehouse.txt', 'w', encoding='utf-8') as f:
            f.write("REPORTES GENERADOS DESDE DATA WAREHOUSE\n")
            f.write("="*50 + "\n\n")
            f.write("1. ANÁLISIS POR ESPECIALIDAD:\n")
            f.write(reporte1.to_string(index=False))
            f.write("\n\n2. PRODUCTIVIDAD POR MÉDICO:\n")
            f.write(reporte2.to_string(index=False))
            f.write("\n\n3. ANÁLISIS TEMPORAL:\n")
            f.write(reporte3.to_string(index=False))
        
        print(f"\nReportes guardados en: reportes/reportes_datawarehouse.txt")
    
    def ejecutar_migracion_completa(self):
        """Ejecuta el proceso completo de migración"""
        
        print("INICIANDO SIMULACIÓN DE MIGRACIÓN A DATA WAREHOUSE")
        print("="*60)
        
        self.conectar_dw()
        self.cargar_datos_limpios()
        self.crear_esquema_dw()
        self.poblar_dimensiones()
        self.poblar_hechos()
        self.generar_reportes_dw()
        
        # Estadísticas finales
        cursor = self.conn.cursor()
        
        # Contar registros en cada tabla
        tablas = ['dim_pacientes', 'dim_medicos', 'dim_especialidades', 'dim_tiempo', 'fact_citas_medicas']
        estadisticas = {}
        
        for tabla in tablas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            estadisticas[tabla] = cursor.fetchone()[0]
        
        print(f"\nESTADÍSTICAS DEL DATA WAREHOUSE:")
        for tabla, count in estadisticas.items():
            print(f"  {tabla}: {count:,} registros")
        
        self.conn.close()
        
        print(f"\nMIGRACIÓN COMPLETADA EXITOSAMENTE")
        print(f"Base de datos creada en: resultados/hospital_datawarehouse.db")

def main():
    simulator = DataWarehouseSimulator()
    simulator.ejecutar_migracion_completa()

if __name__ == "__main__":
    main()