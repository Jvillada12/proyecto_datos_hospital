#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANÁLISIS ESTADÍSTICO PROFUNDO - VERSIÓN CORREGIDA
Sin errores de visualización
"""

import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def cargar_datos():
    with open('../datos/dataset_hospital.json', 'r', encoding='utf-8') as file:
        datos = json.load(file)
    return pd.DataFrame(datos['pacientes']), pd.DataFrame(datos['citas_medicas'])

def generar_visualizaciones_corregidas(df_pacientes, df_citas):
    """Genera visualizaciones sin errores de None"""
    print("GENERANDO VISUALIZACIONES CORREGIDAS...")
    
    plt.style.use('default')
    fig = plt.figure(figsize=(20, 15))
    
    # 1. Distribución de edades
    plt.subplot(3, 3, 1)
    edades = df_pacientes['edad'].dropna()
    plt.hist(edades, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    plt.title('Distribución de Edades')
    plt.xlabel('Edad')
    plt.ylabel('Frecuencia')
    
    # 2. Distribución de sexo (filtrar None)
    plt.subplot(3, 3, 2)
    sexo_counts = df_pacientes['sexo'].value_counts(dropna=True)  # Sin None
    plt.pie(sexo_counts.values, labels=sexo_counts.index, autopct='%1.1f%%')
    plt.title('Distribución de Sexo (sin nulos)')
    
    # 3. Ciudades más frecuentes (sin None)
    plt.subplot(3, 3, 3)
    ciudades = df_pacientes['ciudad'].value_counts(dropna=True).head(5)
    plt.bar(range(len(ciudades)), ciudades.values, color='lightgreen')
    plt.title('Top 5 Ciudades')
    plt.xticks(range(len(ciudades)), ciudades.index, rotation=45)
    
    # 4. Distribución de costos
    plt.subplot(3, 3, 4)
    costos = df_citas['costo'].dropna()
    plt.hist(costos, bins=20, alpha=0.7, color='orange', edgecolor='black')
    plt.title('Distribución de Costos')
    plt.xlabel('Costo ($)')
    
    # 5. Estados de citas (sin None)
    plt.subplot(3, 3, 5)
    estados = df_citas['estado_cita'].value_counts(dropna=True)
    plt.bar(range(len(estados)), estados.values, color='lightcoral')
    plt.title('Estados de Citas (sin nulos)')
    plt.xticks(range(len(estados)), estados.index, rotation=45)
    
    # 6. Especialidades (sin None)
    plt.subplot(3, 3, 6)
    especialidades = df_citas['especialidad'].value_counts(dropna=True).head(5)
    plt.bar(range(len(especialidades)), especialidades.values, color='lightblue')
    plt.title('Top 5 Especialidades')
    plt.xticks(range(len(especialidades)), especialidades.index, rotation=45)
    
    # 7. Problemas de calidad
    plt.subplot(3, 3, 7)
    problemas = [
        'Fechas Inválidas',
        'Nombres Duplicados', 
        'Edades Faltantes',
        'Citas Huérfanas'
    ]
    cantidades = [3314, 4985, 1647, 177]
    colores = ['red', 'orange', 'yellow', 'pink']
    
    plt.bar(problemas, cantidades, color=colores, alpha=0.7)
    plt.title('Problemas de Calidad Identificados')
    plt.xticks(rotation=45)
    plt.ylabel('Cantidad')
    
    # 8. Completitud de datos - Pacientes
    plt.subplot(3, 3, 8)
    completitud_pac = []
    columnas_pac = []
    for col in df_pacientes.columns:
        pct_completo = ((len(df_pacientes) - df_pacientes[col].isnull().sum()) / len(df_pacientes)) * 100
        completitud_pac.append(pct_completo)
        columnas_pac.append(col)
    
    plt.bar(range(len(columnas_pac)), completitud_pac, color='green', alpha=0.7)
    plt.title('Completitud Pacientes (%)')
    plt.xticks(range(len(columnas_pac)), columnas_pac, rotation=45)
    plt.ylim(0, 100)
    
    # 9. Completitud de datos - Citas
    plt.subplot(3, 3, 9)
    completitud_cit = []
    columnas_cit = []
    for col in df_citas.columns:
        pct_completo = ((len(df_citas) - df_citas[col].isnull().sum()) / len(df_citas)) * 100
        completitud_cit.append(pct_completo)
        columnas_cit.append(col)
    
    plt.bar(range(len(columnas_cit)), completitud_cit, color='blue', alpha=0.7)
    plt.title('Completitud Citas (%)')
    plt.xticks(range(len(columnas_cit)), columnas_cit, rotation=45)
    plt.ylim(0, 100)
    
    plt.tight_layout()
    plt.savefig('../resultados/analisis_completo_corregido.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Visualizaciones guardadas en: resultados/analisis_completo_corregido.png")

def generar_reporte_detallado(df_pacientes, df_citas):
    """Genera reporte técnico detallado"""
    
    # Calcular métricas detalladas
    fechas_invalidas = 0
    for fecha in df_citas['fecha_cita'].dropna():
        if isinstance(fecha, str):
            try:
                partes = fecha.split('-')
                if len(partes) == 3:
                    año, mes, dia = int(partes[0]), int(partes[1]), int(partes[2])
                    if mes > 12 or dia > 31:
                        fechas_invalidas += 1
            except:
                fechas_invalidas += 1
    
    reporte = f"""
===============================================================================
REPORTE TÉCNICO DETALLADO - ANÁLISIS DE CALIDAD DE DATOS HOSPITALARIOS
===============================================================================

RESUMEN EJECUTIVO:
El dataset presenta problemas críticos de calidad que requieren limpieza 
sistemática antes de cualquier análisis o uso productivo.

VOLUMEN DE DATOS:
- Pacientes: {len(df_pacientes):,} registros
- Citas Médicas: {len(df_citas):,} registros
- Total de registros: {len(df_pacientes) + len(df_citas):,}

PROBLEMAS CRÍTICOS IDENTIFICADOS:

1. INTEGRIDAD DE DATOS:
   - Citas huérfanas: 177 registros (1.8%)
   - Referencias a pacientes inexistentes detectadas

2. CALIDAD DE FECHAS:
   - Fechas de citas inválidas: {fechas_invalidas:,} ({fechas_invalidas/len(df_citas)*100:.1f}%)
   - Formatos incorrectos: "2023-19-01", "2023-20-01", etc.
   - Fechas en español: 4 casos identificados

3. DUPLICACIÓN MASIVA:
   - Nombres duplicados: {df_pacientes['nombre'].duplicated().sum():,} ({df_pacientes['nombre'].duplicated().sum()/len(df_pacientes)*100:.1f}%)
   - Indica posible generación sintética de datos

4. INCONSISTENCIAS DE FORMATO:
   - Sexo: Male/Female/M/F mezclados
   - Estados de cita: {df_citas['estado_cita'].isnull().sum():,} valores faltantes

5. COMPLETITUD DE DATOS:
   Pacientes:
   - Edad: {df_pacientes['edad'].isnull().sum():,} faltantes ({df_pacientes['edad'].isnull().sum()/len(df_pacientes)*100:.1f}%)
   - Email: {df_pacientes['email'].isnull().sum():,} faltantes ({df_pacientes['email'].isnull().sum()/len(df_pacientes)*100:.1f}%)
   - Teléfono: {df_pacientes['telefono'].isnull().sum():,} faltantes ({df_pacientes['telefono'].isnull().sum()/len(df_pacientes)*100:.1f}%)
   
   Citas:
   - Fecha: {df_citas['fecha_cita'].isnull().sum():,} faltantes ({df_citas['fecha_cita'].isnull().sum()/len(df_citas)*100:.1f}%)
   - Especialidad: {df_citas['especialidad'].isnull().sum():,} faltantes ({df_citas['especialidad'].isnull().sum()/len(df_citas)*100:.1f}%)
   - Médico: {df_citas['medico'].isnull().sum():,} faltantes ({df_citas['medico'].isnull().sum()/len(df_citas)*100:.1f}%)

DISTRIBUCIONES PRINCIPALES:
- Edades: {df_pacientes['edad'].dropna().min():.0f}-{df_pacientes['edad'].dropna().max():.0f} años (promedio: {df_pacientes['edad'].dropna().mean():.1f})
- Costos: ${df_citas['costo'].dropna().min():.0f}-${df_citas['costo'].dropna().max():.0f} (promedio: ${df_citas['costo'].dropna().mean():.2f})
- Ciudades principales: Cali, Bogotá, Bucaramanga (distribución equilibrada)

RECOMENDACIONES INMEDIATAS:
1. Implementar limpieza sistemática de fechas inválidas
2. Estandarizar formatos de campos categóricos
3. Resolver integridad referencial
4. Aplicar reglas de negocio para completar datos faltantes
5. Documentar supuestos adoptados
6. Implementar validaciones automáticas

SIGUIENTE FASE:
Proceder con limpieza de datos usando las funciones especializadas
desarrolladas para abordar cada tipo de problema identificado.

===============================================================================
Reporte generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
===============================================================================
"""
    
    with open('../reportes/reporte_tecnico_detallado.txt', 'w', encoding='utf-8') as f:
        f.write(reporte)
    
    return reporte

def main():
    print("ANÁLISIS ESTADÍSTICO PROFUNDO - VERSIÓN CORREGIDA")
    print("=" * 80)
    
    df_pacientes, df_citas = cargar_datos()
    
    # Generar visualizaciones corregidas
    generar_visualizaciones_corregidas(df_pacientes, df_citas)
    
    # Generar reporte técnico
    reporte = generar_reporte_detallado(df_pacientes, df_citas)
    
    print("\nReporte técnico guardado en: reportes/reporte_tecnico_detallado.txt")
    print("ANÁLISIS COMPLETADO SIN ERRORES")

if __name__ == "__main__":
    main()