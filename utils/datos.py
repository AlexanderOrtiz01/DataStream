# -*- coding: utf-8 -*-
"""Carga y limpieza del dataset y metadatos (descripciones de cada campo).

Dataset: "Data Analyst Jobs" (ofertas de Data Analyst publicadas en Glassdoor).
El CSV original (data/DataAnalyst.csv) viene "sucio": el salario es texto
(`$37K-$66K (Glassdoor est.)`), los valores faltantes estan marcados como `-1`,
la valoracion viene pegada al nombre de la empresa, etc. Aqui se transforma en
un DataFrame limpio y tipado que usan todas las secciones.
"""
import os
import re
import unicodedata
import numpy as np
import pandas as pd
import streamlit as st

# Ruta absoluta al CSV (independiente del directorio de ejecucion)
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_DATASET = os.path.join(_BASE, "data", "DataAnalyst.csv")

# Anio de referencia del scraping (para calcular la antiguedad de la empresa)
_ANIO_REFERENCIA = 2020

# Descripcion legible de cada campo del dataset YA LIMPIO
DESCRIPCIONES = {
    "codigo": "Codigo identificador unico de cada oferta de empleo (formato DA####).",
    "puesto": "Titulo del puesto de Data Analyst tal como lo publico la empresa.",
    "empresa": "Nombre de la empresa que publica la oferta.",
    "sector": "Sector economico general de la empresa (ej. Finance, Health Care).",
    "industria": "Industria especifica dentro del sector (ej. Internet, IT Services).",
    "tipo_propiedad": "Tipo de propiedad de la empresa (privada, publica, sin fines de lucro...).",
    "tamano_empresa": "Rango de numero de empleados de la empresa.",
    "ingresos": "Rango de ingresos anuales estimados de la empresa (en USD).",
    "ciudad": "Ciudad donde se ofrece el puesto.",
    "estado": "Estado (EE.UU.) donde se ofrece el puesto.",
    "sede": "Ubicacion de la sede central (headquarters) de la empresa.",
    "anio_fundacion": "Anio en que se fundo la empresa.",
    "antiguedad_empresa": f"Antiguedad de la empresa en anios (calculada a {_ANIO_REFERENCIA}).",
    "valoracion": "Valoracion de la empresa por sus empleados en Glassdoor (escala 1 a 5).",
    "salario_min_k": "Extremo inferior del salario anual estimado, en miles de USD.",
    "salario_max_k": "Extremo superior del salario anual estimado, en miles de USD.",
    "salario_prom_k": "Punto medio del salario anual estimado, en miles de USD.",
    "aplicacion_facil": "Indica si la oferta permite postulacion rapida 'Easy Apply' (Si/No).",
}

# Nombre de la columna que actua como codigo/identificador
COLUMNA_CODIGO = "codigo"

# Columnas categoricas de muy alta cardinalidad o tipo identificador: se excluyen
# de los selectores de graficos/modelado (siguen visibles en "Descripcion de campos").
_CATEGORICAS_EXCLUIDAS = {COLUMNA_CODIGO, "puesto", "empresa", "ciudad", "sede"}

_TXT_DESCONOCIDO = "Desconocido"


# --------------------------------------------------------------------------- #
# Limpieza del dataset crudo
# --------------------------------------------------------------------------- #
def _parsear_salario(texto: str):
    """Extrae (min, max) en miles de USD de cadenas como '$37K-$66K (...)'."""
    nums = re.findall(r"(\d+)K", str(texto))
    if len(nums) >= 2:
        return float(nums[0]), float(nums[1])
    return np.nan, np.nan


def _limpiar_categorica(serie: pd.Series) -> pd.Series:
    """Convierte marcadores de faltante ('-1', 'Unknown', vacio) en 'Desconocido'."""
    s = serie.astype(str).str.strip()
    faltantes = {"-1", "unknown", "unknown / non-applicable", "nan", ""}
    return s.where(~s.str.lower().isin(faltantes), _TXT_DESCONOCIDO)


def _limpiar(crudo: pd.DataFrame) -> pd.DataFrame:
    """Transforma el CSV crudo de Glassdoor en un DataFrame limpio y tipado."""
    d = crudo.copy()

    # Salario: de texto a tres columnas numericas (miles de USD)
    sal = d["Salary Estimate"].map(_parsear_salario)
    d["salario_min_k"] = [s[0] for s in sal]
    d["salario_max_k"] = [s[1] for s in sal]
    d["salario_prom_k"] = (d["salario_min_k"] + d["salario_max_k"]) / 2

    # Empresa: el nombre trae la valoracion pegada tras un salto de linea
    empresa = d["Company Name"].astype(str).str.split("\n").str[0].str.strip()

    # Valoracion: -1 -> NaN
    valoracion = pd.to_numeric(d["Rating"], errors="coerce")
    valoracion = valoracion.where(valoracion >= 0, np.nan)

    # Fundacion / antiguedad: -1 -> NaN
    fundacion = pd.to_numeric(d["Founded"], errors="coerce")
    fundacion = fundacion.where(fundacion > 0, np.nan)
    antiguedad = _ANIO_REFERENCIA - fundacion

    # Ubicacion -> ciudad, estado
    partes = d["Location"].astype(str).str.split(",", n=1, expand=True)
    ciudad = partes[0].str.strip()
    estado = (partes[1].str.strip() if partes.shape[1] > 1 else ciudad)
    estado = estado.fillna(ciudad)

    # Easy Apply: 'True' -> Si, resto -> No
    aplicacion = np.where(d["Easy Apply"].astype(str).str.strip() == "True", "Si", "No")

    limpio = pd.DataFrame({
        "codigo": [f"DA{int(i):04d}" for i in d["Unnamed: 0"]],
        "puesto": d["Job Title"].astype(str).str.strip(),
        "empresa": _limpiar_categorica(empresa),
        "sector": _limpiar_categorica(d["Sector"]),
        "industria": _limpiar_categorica(d["Industry"]),
        "tipo_propiedad": _limpiar_categorica(d["Type of ownership"]),
        "tamano_empresa": _limpiar_categorica(d["Size"]),
        "ingresos": _limpiar_categorica(d["Revenue"]),
        "ciudad": ciudad,
        "estado": estado,
        "sede": _limpiar_categorica(d["Headquarters"]),
        "anio_fundacion": fundacion,
        "antiguedad_empresa": antiguedad,
        "valoracion": valoracion.round(1),
        "salario_min_k": d["salario_min_k"],
        "salario_max_k": d["salario_max_k"],
        "salario_prom_k": d["salario_prom_k"],
        "aplicacion_facil": aplicacion,
    })

    # Descarta filas sin salario valido (el unico marcador '-1' del archivo)
    limpio = limpio.dropna(subset=["salario_min_k", "salario_max_k"]).reset_index(drop=True)
    return limpio


@st.cache_data
def cargar_datos() -> pd.DataFrame:
    """Carga y limpia el dataset de empleos de Data Analyst (cacheado)."""
    crudo = pd.read_csv(RUTA_DATASET, encoding="utf-8")
    return _limpiar(crudo)


def columnas_numericas(df: pd.DataFrame) -> list:
    """Devuelve las columnas cuantitativas (excluye el codigo si fuera numerico)."""
    cols = df.select_dtypes(include=["number"]).columns.tolist()
    return [c for c in cols if c != COLUMNA_CODIGO]


def columnas_categoricas(df: pd.DataFrame) -> list:
    """Columnas categoricas utiles (excluye identificadores y muy alta cardinalidad)."""
    cols = df.select_dtypes(exclude=["number"]).columns.tolist()
    return [c for c in cols if c not in _CATEGORICAS_EXCLUIDAS]


def descripcion_de(campo: str) -> str:
    """Descripcion textual de un campo."""
    return DESCRIPCIONES.get(campo, "Sin descripcion disponible.")


# --------------------------------------------------------------------------- #
# Deteccion automatica de columnas identificadoras (id / codigo / code / ...)
# Usada por la seccion de carga de archivos del usuario.
# --------------------------------------------------------------------------- #

# Palabras que, como token del nombre de la columna, sugieren un identificador.
PALABRAS_CODIGO = {
    "id", "ids", "cod", "codigo", "code", "codes", "clave", "key", "llave",
    "identificador", "identifier", "folio", "sku", "ref", "referencia",
    "reference", "dni", "ruc", "nif", "cif", "cedula", "matricula",
    "expediente", "ticket", "isbn", "ean", "upc", "uuid", "guid", "pk",
    "serial", "placa", "patente",
}


def _normalizar(nombre: str) -> str:
    """Pasa a minusculas, quita acentos y unifica separadores en espacios."""
    txt = str(nombre).strip().lower()
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    return re.sub(r"[_\-\.\s/]+", " ", txt).strip()


def _nombre_es_codigo(nombre: str) -> bool:
    """True si el NOMBRE de la columna sugiere un identificador/codigo."""
    norm = _normalizar(nombre)
    if not norm:
        return False
    tokens = norm.split(" ")
    # Coincidencia por token completo (cubre "id", "cod_oferta", "job id"...)
    if any(t in PALABRAS_CODIGO for t in tokens):
        return True
    # Coincidencia por prefijo/sufijo pegado (cubre "idcliente", "codoferta")
    pega = norm.replace(" ", "")
    return bool(re.match(r"^(id|cod|codigo|code|uuid|guid)", pega) or
                re.search(r"(id|cod|codigo|code)$", pega))


def detectar_columnas_codigo(df: pd.DataFrame) -> list:
    """Devuelve las columnas que parecen identificadores/codigos.

    Combina dos senales:
      1. El nombre sugiere un codigo (id, cod, codigo, code, clave, sku, ...).
      2. La columna es practicamente unica (>= 90% de valores distintos),
         tipica de claves primarias aunque el nombre no lo indique.
    Las que cumplen la senal de nombre van primero.
    """
    n = len(df)
    por_nombre, por_unicidad = [], []
    for col in df.columns:
        if _nombre_es_codigo(col):
            por_nombre.append(col)
            continue
        # Senal secundaria: columna casi unica Y "corta" (tipo clave), nunca
        # texto libre (descripciones, comentarios) aunque sean todos distintos.
        try:
            ratio_unico = df[col].nunique(dropna=True) / n if n else 0
        except TypeError:  # columnas no hashables
            continue
        if ratio_unico >= 0.9 and n > 1 and _parece_clave_corta(df[col]):
            por_unicidad.append(col)
    return por_nombre + por_unicidad


def _parece_clave_corta(serie: pd.Series) -> bool:
    """True si los valores son cortos (numericos o cadenas <= 40 chars)."""
    if pd.api.types.is_numeric_dtype(serie):
        return True
    largo_max = serie.dropna().astype(str).str.len().max()
    return bool(pd.notna(largo_max) and largo_max <= 40)
