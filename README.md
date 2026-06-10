# 💼 DataStream — Aplicación de Ciencia de Datos

**Técnica Electiva I · Ciencia de Datos — Ciclo I-2026**
Tarea Laboratorio I y II · Cómputo 3

Aplicación web construida con **Streamlit** que integra un flujo completo de Ciencia
de Datos sobre un conjunto de datos real de **ofertas de empleo de Data Analyst**
(Glassdoor). Cubre el 100 % de la rúbrica de las Tareas 1 y 2 mediante una barra de
navegación con 7 opciones.

## ▶️ Cómo ejecutar

```powershell
# 1. (opcional) Crear y activar un entorno virtual
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
streamlit run app.py
```

La app abre en `http://localhost:8501`.

## 🔑 Funciones de IA

Las opciones **6 (Sentimientos)** y **7 (Interfaz IA)** pueden usar un modelo
de **IA generativa**. Configura tu API key de cualquiera de estas formas:

- En la **barra lateral** → *Configurar IA* (recomendado).
- Variable de entorno: `setx IA_API_KEY "tu_clave"`.
- Archivo `.streamlit/secrets.toml` con `IA_API_KEY = "tu_clave"`.

Sin API key, ambas opciones siguen funcionando con motores internos (analizador
léxico de sentimientos y motor de preguntas frecuentes).

## 🗺️ Mapeo con la rúbrica

### Tarea 1
| Opción | Sección | Rúbrica |
|---|---|---|
| 1 | Inicio | Opción 1: Inicio |
| 2 | Análisis Exploratorio | (30%) descripción del dataset y de campos, navegador, **buscador por código (bonus)**, graficador e hipótesis con conclusión |
| 3 | Aprendizaje Automático | (30%) ≥2 algoritmos, ≥2 variables objetivo, ≥2 predictoras, % train/test, gráfica train+test, métricas con `st.metric` |
| 4 | Sistema de Recomendación | (30%) recomendador de empleos basado en contenido |
| 7 | Interfaz IA | Pregunta (10%) |

### Tarea 2
| Opción | Sección | Rúbrica |
|---|---|---|
| 5 | Carga de Archivos | (40%) carga CSV/Excel y genera gráficos |
| 6 | Sentimientos y Scraping | (50%) lee opiniones de la web y analiza sentimientos |
| 7 | Interfaz IA | Pregunta o Interfaz IA (10%) |

## 📁 Estructura

```
DataStream/
├── app.py                 # Entrada y barra de navegación
├── data/DataAnalyst.csv   # Dataset crudo (Glassdoor, Data Analyst Jobs)
├── secciones/             # Una opción de la rúbrica por archivo
│   ├── inicio.py
│   ├── exploratorio.py
│   ├── aprendizaje.py
│   ├── recomendacion.py
│   ├── carga_archivos.py
│   ├── sentimientos.py
│   └── interfaz_ia.py
├── utils/                 # Datos (carga + limpieza), IA, sentimiento, scraping
├── requirements.txt
└── README.md
```

## 📊 Dataset de empleos (Data Analyst Jobs · Glassdoor)

Dataset real con **2 252 ofertas** de Data Analyst. El CSV original viene "sucio"
(salario como texto `$37K-$66K`, valores faltantes marcados como `-1`, la valoración
pegada al nombre de la empresa, etc.) y `utils/datos.py` lo **limpia y tipa**
automáticamente en 18 campos: `codigo`, `puesto`, `empresa`, `sector`, `industria`,
`tipo_propiedad`, `tamano_empresa`, `ingresos`, `ciudad`, `estado`, `sede`,
`anio_fundacion`, `antiguedad_empresa`, `valoracion`, `salario_min_k`,
`salario_max_k`, `salario_prom_k`, `aplicacion_facil`.
