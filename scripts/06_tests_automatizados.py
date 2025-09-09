#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PASO 6: SISTEMA DE TESTS AUTOMÁTICOS AVANZADOS
Suite completa de tests para validación continua
"""

import pandas as pd
import pytest
import json
from datetime import datetime, date
import numpy as np

class TestSuiteAvanzado:
    """Suite completa de tests para datos hospitalarios"""
    
    @classmethod
    def setup_class(cls):
        """Configuración inicial para todos los tests"""
        with open('../resultados/dataset_hospital_limpio.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        cls.df_pacientes = pd.DataFrame(datos['pacientes'])
        cls.df_citas = pd.DataFrame(datos['citas_medicas'])
    
    def test_integridad_estructural(self):
        """Test de integridad estructural de las tablas"""
        # Verificar que las tablas no estén vacías
        assert len(self.df_pacientes) > 0, "Tabla pacientes está vacía"
        assert len(self.df_citas) > 0, "Tabla citas está vacía"
        
        # Verificar columnas esperadas
        cols_esperadas_pac = ['id_paciente', 'nombre', 'fecha_nacimiento', 'edad', 'sexo', 'email', 'telefono', 'ciudad']
        cols_esperadas_citas = ['id_cita', 'id_paciente', 'fecha_cita', 'especialidad', 'medico', 'costo', 'estado_cita']
        
        assert all(col in self.df_pacientes.columns for col in cols_esperadas_pac), "Faltan columnas en pacientes"
        assert all(col in self.df_citas.columns for col in cols_esperadas_citas), "Faltan columnas en citas"
    
    def test_unicidad_ids(self):
        """Test de unicidad de IDs"""
        # IDs de pacientes únicos
        ids_pacientes = self.df_pacientes['id_paciente']
        assert ids_pacientes.nunique() == len(ids_pacientes), "IDs de pacientes duplicados"
        
        # IDs de citas únicos
        ids_citas = self.df_citas['id_cita']
        assert ids_citas.nunique() == len(ids_citas), "IDs de citas duplicados"
    
    def test_integridad_referencial(self):
        """Test de integridad referencial"""
        pacientes_ids = set(self.df_pacientes['id_paciente'])
        citas_paciente_ids = set(self.df_citas['id_paciente'])
        
        # Todas las citas deben tener paciente válido
        citas_huerfanas = citas_paciente_ids - pacientes_ids
        assert len(citas_huerfanas) == 0, f"Citas huérfanas encontradas: {citas_huerfanas}"
    
    def test_valores_sexo_validos(self):
        """Test de valores válidos en campo sexo"""
        valores_validos = {'M', 'F', None}
        valores_sexo = set(self.df_pacientes['sexo'].dropna())
        
        assert valores_sexo.issubset({'M', 'F'}), f"Valores inválidos en sexo: {valores_sexo - {'M', 'F'}}"
    
    def test_rangos_edad_validos(self):
        """Test de rangos válidos de edad"""
        edades = self.df_pacientes['edad'].dropna()
        
        assert (edades >= 0).all(), "Edades negativas encontradas"
        assert (edades <= 120).all(), "Edades mayores a 120 años encontradas"
    
    def test_estados_cita_validos(self):
        """Test de estados de cita válidos"""
        estados_validos = {'Completada', 'Cancelada', 'Reprogramada'}
        estados_cita = set(self.df_citas['estado_cita'].dropna())
        
        assert estados_cita.issubset(estados_validos), f"Estados inválidos: {estados_cita - estados_validos}"
    
    def test_fechas_nacimiento_validas(self):
        """Test de fechas de nacimiento válidas"""
        for idx, fecha in enumerate(self.df_pacientes['fecha_nacimiento'].dropna()):
            try:
                fecha_parsed = pd.to_datetime(fecha)
                assert fecha_parsed.year >= 1900, f"Fecha muy antigua en fila {idx}: {fecha}"
                assert fecha_parsed.year <= datetime.now().year, f"Fecha futura en fila {idx}: {fecha}"
            except:
                assert False, f"Formato de fecha inválido en fila {idx}: {fecha}"
    
    def test_fechas_cita_validas(self):
        """Test de fechas de citas válidas"""
        for idx, fecha in enumerate(self.df_citas['fecha_cita'].dropna()):
            try:
                fecha_parsed = pd.to_datetime(fecha)
                assert fecha_parsed.year >= 2020, f"Fecha de cita muy antigua en fila {idx}: {fecha}"
                assert fecha_parsed.year <= 2030, f"Fecha de cita muy futura en fila {idx}: {fecha}"
            except:
                assert False, f"Formato de fecha de cita inválido en fila {idx}: {fecha}"
    
    def test_costos_validos(self):
        """Test de costos válidos"""
        costos = self.df_citas['costo'].dropna()
        
        assert (costos > 0).all(), "Costos negativos o cero encontrados"
        assert (costos <= 1000).all(), "Costos excesivamente altos encontrados"
    
    def test_consistencia_edad_fecha_nacimiento(self):
        """Test de consistencia entre edad y fecha de nacimiento"""
        tolerancia = 2  # años
        
        for idx, row in self.df_pacientes.iterrows():
            if pd.notna(row['edad']) and pd.notna(row['fecha_nacimiento']):
                fecha_nac = pd.to_datetime(row['fecha_nacimiento'])
                edad_calculada = (datetime.now() - fecha_nac).days // 365
                diferencia = abs(edad_calculada - row['edad'])
                
                assert diferencia <= tolerancia, f"Inconsistencia edad-fecha en fila {idx}: edad={row['edad']}, calculada={edad_calculada}"
    
    def test_emails_formato_valido(self):
        """Test de formato válido de emails"""
        import re
        patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for idx, email in enumerate(self.df_pacientes['email'].dropna()):
            assert re.match(patron_email, email), f"Email inválido en fila {idx}: {email}"
    
    def test_volumenes_esperados(self):
        """Test de volúmenes esperados de datos"""
        # Debe haber datos significativos
        assert len(self.df_pacientes) >= 1000, "Volumen de pacientes muy bajo"
        assert len(self.df_citas) >= 1000, "Volumen de citas muy bajo"
        
        # Ratio citas/pacientes razonable
        ratio = len(self.df_citas) / len(self.df_pacientes)
        assert 1 <= ratio <= 5, f"Ratio citas/pacientes anómalo: {ratio:.2f}"

def ejecutar_tests_completos():
    """Ejecuta suite completa de tests"""
    
    print("EJECUTANDO SUITE COMPLETA DE TESTS AUTOMÁTICOS")
    print("="*60)
    
    # Crear instancia de tests
    test_suite = TestSuiteAvanzado()
    test_suite.setup_class()
    
    # Lista de tests a ejecutar
    tests = [
        ('Integridad Estructural', test_suite.test_integridad_estructural),
        ('Unicidad de IDs', test_suite.test_unicidad_ids),
        ('Integridad Referencial', test_suite.test_integridad_referencial),
        ('Valores de Sexo', test_suite.test_valores_sexo_validos),
        ('Rangos de Edad', test_suite.test_rangos_edad_validos),
        ('Estados de Cita', test_suite.test_estados_cita_validos),
        ('Fechas de Nacimiento', test_suite.test_fechas_nacimiento_validas),
        ('Fechas de Citas', test_suite.test_fechas_cita_validas),
        ('Costos Válidos', test_suite.test_costos_validos),
        ('Consistencia Edad-Fecha', test_suite.test_consistencia_edad_fecha_nacimiento),
        ('Formato de Emails', test_suite.test_emails_formato_valido),
        ('Volúmenes Esperados', test_suite.test_volumenes_esperados)
    ]
    
    resultados = []
    
    for nombre_test, test_func in tests:
        try:
            test_func()
            resultados.append((nombre_test, "PASS", "Test exitoso"))
            print(f"✓ {nombre_test}: PASS")
        except AssertionError as e:
            resultados.append((nombre_test, "FAIL", str(e)))
            print(f"✗ {nombre_test}: FAIL - {e}")
        except Exception as e:
            resultados.append((nombre_test, "ERROR", str(e)))
            print(f"⚠ {nombre_test}: ERROR - {e}")
    
    # Resumen final
    total_tests = len(resultados)
    tests_pasados = sum(1 for _, resultado, _ in resultados if resultado == "PASS")
    
    print(f"\n" + "="*60)
    print(f"RESUMEN DE TESTS: {tests_pasados}/{total_tests} PASARON")
    print(f"Porcentaje de éxito: {(tests_pasados/total_tests)*100:.1f}%")
    
    # Guardar reporte de tests
    reporte_tests = f"""
REPORTE DE TESTS AUTOMÁTICOS
============================

Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total de tests: {total_tests}
Tests pasados: {tests_pasados}
Tasa de éxito: {(tests_pasados/total_tests)*100:.1f}%

RESULTADOS DETALLADOS:
"""
    
    for nombre, resultado, detalle in resultados:
        reporte_tests += f"\n{nombre}: {resultado}"
        if resultado != "PASS":
            reporte_tests += f" - {detalle}"
    
    reporte_tests += f"""

CONCLUSIONES:
{"Todos los tests pasaron exitosamente. Los datos están validados y listos para producción." if tests_pasados == total_tests else "Algunos tests fallaron. Revisar problemas identificados antes de usar en producción."}

RECOMENDACIONES:
- Ejecutar estos tests automáticamente antes de cada deploy
- Configurar alertas para fallos de tests
- Documentar cualquier excepción justificada
- Actualizar tests cuando cambien los requisitos de negocio
"""
    
    with open('../reportes/reporte_tests_automaticos.txt', 'w', encoding='utf-8') as f:
        f.write(reporte_tests)
    
    print(f"\nReporte guardado en: reportes/reporte_tests_automaticos.txt")
    
    return tests_pasados == total_tests

if __name__ == "__main__":
    exito = ejecutar_tests_completos()
    if exito:
        print("\nTODOS LOS TESTS PASARON - DATOS VALIDADOS")
    else:
        print("\nALGUNOS TESTS FALLARON - REVISAR PROBLEMAS")