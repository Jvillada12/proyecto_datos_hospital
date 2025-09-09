#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PASO 3: LIMPIEZA AVANZADA DE DATOS
Sistema robusto para manejar los problemas críticos identificados
"""

import pandas as pd
import numpy as np
import json
import re
from datetime import datetime, date
import warnings
warnings.filterwarnings('ignore')

class HospitalDataCleaner:
    """Sistema avanzado de limpieza de datos hospitalarios"""
    
    def __init__(self, df_pacientes, df_citas):
        self.df_pacientes_original = df_pacientes.copy()
        self.df_citas_original = df_citas.copy()
        self.df_pacientes = df_pacientes.copy()
        self.df_citas = df_citas.copy()
        self.log_limpieza = []
        self.supuestos = []
        
    def log(self, accion, detalles):
        """Registra acciones de limpieza"""
        entrada = f"{datetime.now().strftime('%H:%M:%S')} - {accion}: {detalles}"
        self.log_limpieza.append(entrada)
        print(f"  {accion}: {detalles}")
    
    def supuesto(self, descripcion):
        """Registra supuestos adoptados"""
        self.supuestos.append(descripcion)
        print(f"  SUPUESTO: {descripcion}")
    
    def limpiar_sexo(self):
        """Estandariza valores de sexo"""
        print("\n1. ESTANDARIZANDO CAMPO SEXO")
        
        antes = self.df_pacientes['sexo'].value_counts(dropna=False)
        
        # Mapeo de estandarización
        mapeo_sexo = {
            'Male': 'M',
            'Female': 'F',
            'M': 'M',
            'F': 'F'
        }
        
        self.df_pacientes['sexo'] = self.df_pacientes['sexo'].map(mapeo_sexo)
        
        despues = self.df_pacientes['sexo'].value_counts(dropna=False)
        
        self.log("Sexo estandarizado", f"Male/Female convertido a M/F")
        self.supuesto("Valores null en sexo se mantienen para decisión de negocio posterior")
        
        return antes, despues
    
    def limpiar_fechas_nacimiento(self):
        """Limpia fechas de nacimiento con múltiples formatos"""
        print("\n2. LIMPIANDO FECHAS DE NACIMIENTO")
        
        def procesar_fecha_nacimiento(fecha):
            if pd.isna(fecha):
                return None
            
            try:
                fecha_str = str(fecha)
                
                # Formato estándar YYYY-MM-DD
                if re.match(r'^\d{4}-\d{2}-\d{2}$', fecha_str):
                    # Verificar fecha válida
                    partes = fecha_str.split('-')
                    año, mes, dia = int(partes[0]), int(partes[1]), int(partes[2])
                    
                    # Detectar día 33 (error común)
                    if dia == 33:
                        dia = 3  # Asumir que 33 era 03
                        fecha_str = f"{año}-{mes:02d}-{dia:02d}"
                    
                    if mes > 12 or dia > 31:
                        return None
                    
                    return pd.to_datetime(fecha_str).date()
                
                # Formato español: "DD de MMM de YYYY"
                if 'de' in fecha_str:
                    meses = {
                        'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
                        'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
                        'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12',
                        'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04',
                        'may': '05', 'jun': '06', 'jul': '07', 'ago': '08',
                        'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
                    }
                    
                    # Buscar patrón
                    patron = r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})'
                    match = re.search(patron, fecha_str.lower())
                    
                    if match:
                        dia, mes_nombre, año = match.groups()
                        if mes_nombre in meses:
                            fecha_nueva = f"{año}-{meses[mes_nombre]}-{dia.zfill(2)}"
                            return pd.to_datetime(fecha_nueva).date()
                
                return None
                
            except Exception:
                return None
        
        fechas_antes = self.df_pacientes['fecha_nacimiento'].notna().sum()
        
        self.df_pacientes['fecha_nacimiento'] = self.df_pacientes['fecha_nacimiento'].apply(
            procesar_fecha_nacimiento
        )
        
        fechas_despues = self.df_pacientes['fecha_nacimiento'].notna().sum()
        
        self.log("Fechas de nacimiento procesadas", 
                f"Válidas: {fechas_antes} -> {fechas_despues}")
        self.supuesto("Fechas con día 33 se corrigieron a día 03")
        self.supuesto("Fechas en español se convirtieron a formato ISO")
    
    def calcular_edades(self):
        """Calcula edades desde fechas de nacimiento"""
        print("\n3. CALCULANDO Y VALIDANDO EDADES")
        
        def calcular_edad_actual(fecha_nac):
            if pd.isna(fecha_nac):
                return None
            
            try:
                if isinstance(fecha_nac, str):
                    fecha_nac = pd.to_datetime(fecha_nac).date()
                
                hoy = date.today()
                edad = hoy.year - fecha_nac.year
                
                if (hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day):
                    edad -= 1
                
                return edad if 0 <= edad <= 120 else None
                
            except:
                return None
        
        # Calcular edades desde fechas
        edades_calculadas = self.df_pacientes['fecha_nacimiento'].apply(calcular_edad_actual)
        
        # Comparar con edades existentes
        discrepancias = 0
        edades_completadas = 0
        
        for idx, row in self.df_pacientes.iterrows():
            edad_original = row['edad']
            edad_calculada = edades_calculadas[idx]
            
            if pd.notna(edad_calculada):
                if pd.isna(edad_original):
                    # Completar edad faltante
                    self.df_pacientes.loc[idx, 'edad'] = edad_calculada
                    edades_completadas += 1
                elif abs(edad_original - edad_calculada) > 2:
                    # Discrepancia significativa - usar calculada
                    self.df_pacientes.loc[idx, 'edad'] = edad_calculada
                    discrepancias += 1
        
        self.log("Edades procesadas", 
                f"Discrepancias corregidas: {discrepancias}, Completadas: {edades_completadas}")
        self.supuesto("En discrepancias >2 años, se priorizó edad calculada desde fecha nacimiento")
    
    def limpiar_fechas_citas(self):
        """Limpia fechas de citas con problemas masivos de formato"""
        print("\n4. LIMPIANDO FECHAS DE CITAS (PROBLEMA CRÍTICO)")
        
        def procesar_fecha_cita(fecha):
            if pd.isna(fecha):
                return None
            
            try:
                fecha_str = str(fecha)
                
                # Detectar formato YYYY-MM-DD con errores
                if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', fecha_str):
                    partes = fecha_str.split('-')
                    año, mes, dia = int(partes[0]), int(partes[1]), int(partes[2])
                    
                    # Corregir meses inválidos comunes
                    if mes > 12:
                        # Patrones detectados: 13->01, 14->02, 15->03, etc.
                        if mes <= 24:
                            mes = mes - 12
                        else:
                            return None  # Muy inválido
                    
                    # Validar día
                    if dia > 31 or dia < 1:
                        return None
                    
                    # Validar año razonable
                    if año < 2020 or año > 2030:
                        return None
                    
                    try:
                        return pd.to_datetime(f"{año}-{mes:02d}-{dia:02d}").date()
                    except:
                        return None
                
                return None
                
            except:
                return None
        
        fechas_antes = self.df_citas['fecha_cita'].notna().sum()
        fechas_invalidas_antes = 0
        
        # Contar inválidas antes
        for fecha in self.df_citas['fecha_cita'].dropna():
            if isinstance(fecha, str):
                try:
                    partes = fecha.split('-')
                    if len(partes) == 3:
                        mes = int(partes[1])
                        if mes > 12:
                            fechas_invalidas_antes += 1
                except:
                    continue
        
        self.df_citas['fecha_cita'] = self.df_citas['fecha_cita'].apply(procesar_fecha_cita)
        
        fechas_despues = self.df_citas['fecha_cita'].notna().sum()
        
        self.log("Fechas de citas corregidas", 
                f"Antes: {fechas_antes}, Después: {fechas_despues}, Inválidas detectadas: {fechas_invalidas_antes}")
        self.supuesto("Meses >12 se corrigieron restando 12 (ej: mes 13 -> mes 1)")
        self.supuesto("Fechas no corregibles se marcaron como null")
    
    def completar_estados_citas(self):
        """Completa estados de citas faltantes usando lógica de negocio"""
        print("\n5. COMPLETANDO ESTADOS DE CITAS")
        
        estados_antes = self.df_citas['estado_cita'].isnull().sum()
        
        for idx, row in self.df_citas.iterrows():
            if pd.isna(row['estado_cita']):
                # Lógica de negocio para inferir estado
                if pd.notna(row['fecha_cita']) and pd.notna(row['costo']):
                    # Tiene fecha y costo -> probablemente completada
                    self.df_citas.loc[idx, 'estado_cita'] = 'Completada'
                elif pd.isna(row['fecha_cita']):
                    # Sin fecha -> probablemente cancelada
                    self.df_citas.loc[idx, 'estado_cita'] = 'Cancelada'
                else:
                    # Otros casos -> reprogramada
                    self.df_citas.loc[idx, 'estado_cita'] = 'Reprogramada'
        
        estados_despues = self.df_citas['estado_cita'].isnull().sum()
        
        self.log("Estados completados", 
                f"Faltantes: {estados_antes} -> {estados_despues}")
        self.supuesto("Estados inferidos: fecha+costo=Completada, sin fecha=Cancelada, otros=Reprogramada")
    
    def resolver_integridad_referencial(self):
        """Resuelve problemas de integridad referencial"""
        print("\n6. RESOLVIENDO INTEGRIDAD REFERENCIAL")
        
        pacientes_validos = set(self.df_pacientes['id_paciente'])
        citas_huerfanas = []
        
        for idx, row in self.df_citas.iterrows():
            if row['id_paciente'] not in pacientes_validos:
                citas_huerfanas.append(idx)
        
        if citas_huerfanas:
            # Remover citas huérfanas
            self.df_citas = self.df_citas.drop(citas_huerfanas).reset_index(drop=True)
            
            self.log("Integridad referencial restaurada", 
                    f"Citas huérfanas removidas: {len(citas_huerfanas)}")
            self.supuesto("Citas sin paciente válido fueron eliminadas para mantener integridad")
        else:
            self.log("Integridad referencial", "No se encontraron problemas")
    
    def ejecutar_limpieza_completa(self):
        """Ejecuta todo el proceso de limpieza"""
        print("="*80)
        print("INICIANDO LIMPIEZA AVANZADA DE DATOS HOSPITALARIOS")
        print("="*80)
        
        # Estadísticas iniciales
        print(f"\nESTADÍSTICAS INICIALES:")
        print(f"- Pacientes: {len(self.df_pacientes_original):,}")
        print(f"- Citas: {len(self.df_citas_original):,}")
        
        # Ejecutar limpieza paso a paso
        self.limpiar_sexo()
        self.limpiar_fechas_nacimiento()
        self.calcular_edades()
        self.limpiar_fechas_citas()
        self.completar_estados_citas()
        self.resolver_integridad_referencial()
        
        # Estadísticas finales
        print(f"\nESTADÍSTICAS FINALES:")
        print(f"- Pacientes: {len(self.df_pacientes):,}")
        print(f"- Citas: {len(self.df_citas):,}")
        
        print("\n" + "="*80)
        print("LIMPIEZA AVANZADA COMPLETADA")
        print("="*80)
        
        return self.df_pacientes, self.df_citas

def main():
    print("SISTEMA DE LIMPIEZA AVANZADA - DATOS HOSPITALARIOS")
    print("=" * 80)
    
    # Cargar datos
    with open('../datos/dataset_hospital.json', 'r', encoding='utf-8') as file:
        datos = json.load(file)
    
    df_pacientes_original = pd.DataFrame(datos['pacientes'])
    df_citas_original = pd.DataFrame(datos['citas_medicas'])
    
    # Crear instancia del limpiador
    limpiador = HospitalDataCleaner(df_pacientes_original, df_citas_original)
    
    # Ejecutar limpieza
    df_pacientes_clean, df_citas_clean = limpiador.ejecutar_limpieza_completa()
    
    # Guardar datos limpios
    datos_limpios = {
        'pacientes': df_pacientes_clean.to_dict('records'),
        'citas_medicas': df_citas_clean.to_dict('records')
    }
    
    # Convertir fechas a strings para JSON
    for paciente in datos_limpios['pacientes']:
        if paciente['fecha_nacimiento']:
            paciente['fecha_nacimiento'] = str(paciente['fecha_nacimiento'])
    
    for cita in datos_limpios['citas_medicas']:
        if cita['fecha_cita']:
            cita['fecha_cita'] = str(cita['fecha_cita'])
    
    # Exportar
    with open('../resultados/dataset_hospital_limpio.json', 'w', encoding='utf-8') as f:
        json.dump(datos_limpios, f, indent=2, ensure_ascii=False)
    
    df_pacientes_clean.to_csv('../resultados/pacientes_limpio.csv', index=False, encoding='utf-8')
    df_citas_clean.to_csv('../resultados/citas_limpio.csv', index=False, encoding='utf-8')
    
    # Guardar log de limpieza
    with open('../reportes/log_limpieza_avanzada.txt', 'w', encoding='utf-8') as f:
        f.write("LOG DE LIMPIEZA AVANZADA\n")
        f.write("="*50 + "\n\n")
        f.write("ACCIONES REALIZADAS:\n")
        for accion in limpiador.log_limpieza:
            f.write(f"{accion}\n")
        f.write("\nSUPUESTOS ADOPTADOS:\n")
        for supuesto in limpiador.supuestos:
            f.write(f"- {supuesto}\n")
    
    print(f"\nARCHIVOS GENERADOS:")
    print(f"- resultados/dataset_hospital_limpio.json")
    print(f"- resultados/pacientes_limpio.csv")
    print(f"- resultados/citas_limpio.csv")
    print(f"- reportes/log_limpieza_avanzada.txt")

if __name__ == "__main__":
    main()