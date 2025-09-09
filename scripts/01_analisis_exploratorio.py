#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PASO 1: ANÁLISIS EXPLORATORIO DE DATOS HOSPITALARIOS
Identifica problemas de calidad en los datos originales
"""

import pandas as pd
import json
import sys
import os

def cargar_datos():
    """Carga los datos desde el archivo JSON"""
    try:
        with open('../datos/dataset_hospital.json', 'r', encoding='utf-8') as file:
            datos = json.load(file)
        
        df_pacientes = pd.DataFrame(datos['pacientes'])
        df_citas = pd.DataFrame(datos['citas_medicas'])
        
        print("Datos cargados exitosamente:")
        print(f"  - Pacientes: {len(df_pacientes):,} registros")
        print(f"  - Citas: {len(df_citas):,} registros")
        
        return df_pacientes, df_citas
    
    except FileNotFoundError:
        print("ERROR: No se encontró el archivo dataset_hospital.json en la carpeta datos/")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR al cargar datos: {e}")
        sys.exit(1)

def analizar_pacientes(df):
    """Analiza la tabla de pacientes"""
    print("\n" + "="*60)
    print("ANÁLISIS DE LA TABLA PACIENTES")
    print("="*60)
    
    print(f"Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
    print(f"Columnas: {list(df.columns)}")
    
    print("\nPrimeras 3 filas:")
    print(df.head(3).to_string())
    
    print("\nValores faltantes por columna:")
    faltantes = df.isnull().sum()
    for columna, cantidad in faltantes.items():
        porcentaje = (cantidad / len(df)) * 100
        print(f"  {columna}: {cantidad} ({porcentaje:.1f}%)")
    
    print("\nProblemas identificados en sexo:")
    print(df['sexo'].value_counts(dropna=False))
    
    print("\nEjemplos de fechas de nacimiento:")
    fechas_muestra = df['fecha_nacimiento'].dropna().head(10).tolist()
    for i, fecha in enumerate(fechas_muestra, 1):
        print(f"  {i}. {fecha}")

def analizar_citas(df):
    """Analiza la tabla de citas médicas"""
    print("\n" + "="*60)
    print("ANÁLISIS DE LA TABLA CITAS MÉDICAS")
    print("="*60)
    
    print(f"Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
    print(f"Columnas: {list(df.columns)}")
    
    print("\nPrimeras 3 filas:")
    print(df.head(3).to_string())
    
    print("\nValores faltantes por columna:")
    faltantes = df.isnull().sum()
    for columna, cantidad in faltantes.items():
        porcentaje = (cantidad / len(df)) * 100
        print(f"  {columna}: {cantidad} ({porcentaje:.1f}%)")
    
    print("\nEstados de cita únicos:")
    print(df['estado_cita'].value_counts(dropna=False))
    
    print("\nEjemplos de fechas de cita:")
    fechas_muestra = df['fecha_cita'].dropna().head(10).tolist()
    for i, fecha in enumerate(fechas_muestra, 1):
        print(f"  {i}. {fecha}")

def identificar_problemas(df_pacientes, df_citas):
    """Identifica problemas específicos de calidad"""
    print("\n" + "="*60)
    print("PROBLEMAS DE CALIDAD IDENTIFICADOS")
    print("="*60)
    
    problemas = []
    
    # Problema 1: Inconsistencias en sexo
    sexo_invalidos = df_pacientes[~df_pacientes['sexo'].isin(['M', 'F'])]['sexo'].count()
    if sexo_invalidos > 0:
        problemas.append(f"Valores de sexo inconsistentes: {sexo_invalidos} casos")
    
    # Problema 2: Fechas con formato español
    fechas_espanol = 0
    for fecha in df_pacientes['fecha_nacimiento'].dropna():
        if isinstance(fecha, str) and 'de' in fecha:
            fechas_espanol += 1
    
    if fechas_espanol > 0:
        problemas.append(f"Fechas de nacimiento en formato español: {fechas_espanol} casos")
    
    # Problema 3: Fechas de citas inválidas
    fechas_invalidas = 0
    for fecha in df_citas['fecha_cita'].dropna():
        if isinstance(fecha, str):
            try:
                partes = fecha.split('-')
                if len(partes) == 3:
                    año, mes, dia = int(partes[0]), int(partes[1]), int(partes[2])
                    if mes > 12 or dia > 31 or mes < 1 or dia < 1:
                        fechas_invalidas += 1
            except:
                fechas_invalidas += 1
    
    if fechas_invalidas > 0:
        problemas.append(f"Fechas de citas inválidas: {fechas_invalidas} casos")
    
    # Problema 4: Estados faltantes
    estados_faltantes = df_citas['estado_cita'].isnull().sum()
    if estados_faltantes > 0:
        problemas.append(f"Estados de cita faltantes: {estados_faltantes} casos")
    
    print("Resumen de problemas encontrados:")
    for i, problema in enumerate(problemas, 1):
        print(f"  {i}. {problema}")
    
    return problemas

def main():
    print("ANÁLISIS EXPLORATORIO DE DATOS HOSPITALARIOS")
    print("=" * 80)
    
    # Cargar datos
    df_pacientes, df_citas = cargar_datos()
    
    # Analizar cada tabla
    analizar_pacientes(df_pacientes)
    analizar_citas(df_citas)
    
    # Identificar problemas
    problemas = identificar_problemas(df_pacientes, df_citas)
    
    # Guardar resumen
    resumen = f"""
RESUMEN DEL ANÁLISIS EXPLORATORIO

DATOS CARGADOS:
- Pacientes: {len(df_pacientes):,} registros
- Citas: {len(df_citas):,} registros

PROBLEMAS IDENTIFICADOS:
{chr(10).join(f'- {p}' for p in problemas)}

SIGUIENTE PASO: Ejecutar script de limpieza de datos
"""
    
    with open('../reportes/01_resumen_exploratorio.txt', 'w', encoding='utf-8') as f:
        f.write(resumen)
    
    print(f"\nResumen guardado en: reportes/01_resumen_exploratorio.txt")
    print("ANÁLISIS EXPLORATORIO COMPLETADO")

if __name__ == "__main__":
    main()