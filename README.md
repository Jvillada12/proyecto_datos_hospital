# Análisis y Limpieza de Datos Hospitalarios

**Prueba Técnica - Ingeniero de Datos**  
**Desarrollado por:** Johnnatan Villada Flórez  
**Fecha:** Septiembre 2025

## Descripción del Proyecto

Sistema completo de análisis, limpieza y validación de datos hospitalarios que procesa información de 5,010 pacientes y 9,961 citas médicas. El proyecto identifica y resuelve 5,525 problemas críticos de calidad de datos mediante técnicas avanzadas de ingeniería de datos.

## Resultados Principales

- **Score de Calidad General:** 68.2% → 88.6% (+20.4 puntos)
- **Problemas Críticos Resueltos:** 5,525 casos
- **Integridad Referencial:** 98.1% → 100%
- **Tests Automáticos:** 12/12 exitosos
- **Tiempo de Desarrollo:** 6 horas

## Arquitectura del Proyecto

```
proyecto-datos-hospital/
├── datos/                    # Datos originales
│   └── dataset_hospital.json
├── scripts/                  # Código fuente
│   ├── 01_analisis_exploratorio.py
│   ├── 02_analisis_profundo.py
│   ├── 03_limpieza_avanzada.py
│   ├── 04_validacion_final.py
│   ├─  05_dashboard_profesional.py
│   ├── 06_tests_automatizados.py
│   └── 07_simulacion_datawarehouse.py
├── resultados/              # Datos procesados
│   ├── dataset_hospital_limpio.json
│   ├── pacientes_limpio.csv
│   └── citas_limpio.csv
├── reportes/                # Documentación y reportes
│   ├── dashboard_interactivo.html
│   ├── informe_tecnico_completo.txt
│   └── comparacion_antes_despues.png
└── README.md
```

## Instalación y Configuración

### Prerrequisitos
- Python 3.9+
- pip (gestor de paquetes de Python)

### Instalación de Dependencias
```bash
git clone https://github.com/Jvillada12/proyecto_datos_hospital.git
cd proyecto_datos_hospital
pip install pandas numpy matplotlib seaborn plotly pytest
```

## Guía de Ejecución

### Ejecución Completa (Recomendada)
```bash
# 1. Análisis exploratorio inicial
cd scripts
python3 01_analisis_exploratorio.py

# 2. Análisis estadístico profundo
python3 02_analisis_profundo.py

# 3. Proceso de limpieza avanzada
python3 03_limpieza_avanzada.py

# 4. Validación final y métricas
python3 04_validacion_final.py

# 5. Dashboard interactivo
python3 dashboard_profesional.py

# 6. Tests automáticos
python3 06_tests_automatizados.py

# 7. Simulación Data Warehouse
python3 07_simulacion_datawarehouse.py
```

### Ejecución Individual por Módulos

#### Análisis Exploratorio
```bash
python3 01_analisis_exploratorio.py
```
- Carga inicial de datos
- Identificación de problemas básicos
- Estadísticas descriptivas

#### Limpieza de Datos
```bash
python3 03_limpieza_avanzada.py
```
- Proceso sistemático de limpieza
- Corrección de 5,525 problemas
- Exportación de datos limpios

#### Dashboard Interactivo
```bash
python3 dashboard_interactivo_final.py
```
- Visualizaciones profesionales
- KPIs de calidad en tiempo real
- Comparativas antes/después

## Problemas Identificados y Solucionados

### Tabla Pacientes (5,010 registros)
- **Formato de sexo inconsistente:** 2,021 casos (Male/Female → M/F)
- **Edades faltantes:** 1,647 casos (32.9%)
- **Fechas formato español:** 4 casos corregidos
- **Duplicación de nombres:** 4,985 casos identificados

### Tabla Citas (9,961 registros)
- **Fechas inválidas:** 3,314 casos (mes >12 corregidos)
- **Estados faltantes:** 2,542 casos completados
- **Citas huérfanas:** 190 casos eliminados
- **Valores null masivos:** Múltiples campos completados

## Tecnologías Utilizadas

- **Python 3.9+:** Lenguaje principal
- **pandas:** Manipulación de datos
- **numpy:** Operaciones numéricas
- **matplotlib/seaborn:** Visualización básica
- **plotly:** Dashboard interactivo
- **pytest:** Testing automático
- **sqlite3:** Simulación Data Warehouse

## Características Destacadas

### 1. Dashboard Interactivo
- Visualizaciones en tiempo real
- KPIs de calidad automáticos
- Gráficos comparativos antes/después
- Interface web profesional

### 2. Tests Automáticos
- 12 validaciones independientes
- Cobertura 100% de casos críticos
- Integración lista para CI/CD
- Reportes automáticos

### 3. Simulación Data Warehouse
- Esquema estrella completo
- Dimensiones: Pacientes, Médicos, Especialidades, Tiempo
- Tabla de hechos: Citas médicas
- Reportes analíticos de ejemplo

### 4. Documentación Exhaustiva
- Informe técnico completo
- Justificación de cada decisión
- Supuestos claramente documentados
- Métricas detalladas de mejora

## Métricas de Calidad

| Dimensión | Antes | Después | Mejora |
|-----------|--------|---------|--------|
| Completitud | 67.1% | 86.1% | +19.0% |
| Consistencia | 39.4% | 79.6% | +40.2% |
| Integridad | 98.1% | 100.0% | +1.9% |
| **Score General** | **68.2%** | **88.6%** | **+20.4%** |

## Supuestos Principales

1. **Corrección de fechas:** Meses >12 se corrigieron restando 12
2. **Prioridad fecha nacimiento:** En discrepancias, se usó fecha vs edad registrada
3. **Estados de citas:** Inferidos por lógica de negocio (fecha+costo=Completada)
4. **Eliminación huérfanos:** Citas sin paciente válido se removieron
5. **Estandarización:** Formatos unificados para consistencia

## Archivos Generados

### Datos Limpios
- `dataset_hospital_limpio.json`: Dataset completo procesado
- `pacientes_limpio.csv`: Tabla pacientes limpia
- `citas_limpio.csv`: Tabla citas limpia

### Reportes y Visualizaciones
- `dashboard_interactivo.html`: Dashboard web interactivo
- `comparacion_antes_despues.png`: Gráficos comparativos
- `informe_tecnico_completo.txt`: Documentación completa

### Base de Datos
- `hospital_datawarehouse.db`: Simulación Data Warehouse

## Tests y Validaciones

```bash
# Ejecutar tests automáticos
python3 06_tests_automatizados.py
```

**Tests implementados:**
- Integridad estructural
- Unicidad de IDs
- Integridad referencial
- Validación de dominios
- Rangos de valores
- Consistencia cruzada

**Resultado:** 12/12 tests exitosos (100%)

## Uso del Dashboard

1. Ejecutar: `python3 dashboard_profesional.py`
2. Abrir: `reportes/dashboard_interactivo.html`
3. Navegar por las visualizaciones interactivas
4. Analizar KPIs y métricas de calidad

## Contribuciones

Este proyecto fue desarrollado como prueba técnica individual. Para sugerencias o mejoras:

1. Fork del repositorio
2. Crear branch feature
3. Commit de cambios
4. Pull request con descripción detallada

## Licencia

Proyecto desarrollado para fines académicos y/o demostración de capacidades técnicas.

## Contacto

**Johnnatan Villada Flórez**
- GitHub: [@Jvillada12](https://github.com/Jvillada12)
- Proyecto: [proyecto_datos_hospital](https://github.com/Jvillada12/proyecto_datos_hospital)
- Whatsapp: 3006389159
- Correo E: villada.johnnatan@gmail.com
- LinkedIn: https://www.linkedin.com/in/johnnatan-villada-4845952b7
- CV: https://jvillada12.github.io

---

*Desarrollado con Python para demostración de capacidades en Ingeniería de Datos*


