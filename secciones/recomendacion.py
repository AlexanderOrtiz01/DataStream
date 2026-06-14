# -*- coding: utf-8 -*-
"""Opcion 4: Sistema de Recomendacion de empleos (basado en contenido)."""
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

from utils.datos import cargar_datos

_COLS_MOSTRAR = ["puesto", "empresa", "sector", "ciudad", "estado",
                 "salario_min_k", "salario_max_k", "valoracion"]

_CATEGORICAS = ["sector", "tipo_propiedad", "tamano_empresa", "aplicacion_facil"]
_NUMERICAS = ["salario_min_k", "salario_max_k", "salario_prom_k",
              "valoracion", "antiguedad_empresa"]


@st.cache_data
def _matriz_caracteristicas(df: pd.DataFrame):
    """Construye la matriz de caracteristicas (one-hot + numericas normalizadas)."""
    dummies = pd.get_dummies(df[_CATEGORICAS], prefix=_CATEGORICAS)
    # Los faltantes numericos se rellenan con la mediana para no romper el escalado
    num = df[_NUMERICAS].fillna(df[_NUMERICAS].median())
    escalador = MinMaxScaler()
    num = pd.DataFrame(escalador.fit_transform(num),
                       columns=_NUMERICAS, index=df.index)
    matriz = pd.concat([dummies, num], axis=1)
    return matriz.values


def mostrar():
    st.title("Sistema de Recomendacion de Empleos")
    st.write(
        "Sistema de recomendacion **basado en contenido**: a partir de una oferta de "
        "Data Analyst que te interese, encuentra las mas parecidas comparando sector, "
        "tipo y tamano de empresa, salario y valoracion mediante **similitud del "
        "coseno**."
    )

    df = cargar_datos().reset_index(drop=True)
    matriz = _matriz_caracteristicas(df)

    modo = st.radio("Modo de recomendacion",
                    ["Por empleo similar", "Por mis preferencias"], horizontal=True)

    if modo == "Por empleo similar":
        _por_empleo(df, matriz)
    else:
        _por_preferencias(df)


def _por_empleo(df: pd.DataFrame, matriz: np.ndarray):
    nombres = (df["puesto"] + " — " + df["empresa"] + "  (" + df["codigo"] + ")").tolist()
    idx = st.selectbox("Elige una oferta de empleo de interes",
                       range(len(nombres)), format_func=lambda i: str(nombres[i]))
    n = st.slider("Cantidad de recomendaciones", 3, 10, 5)

    base = df.iloc[idx]
    valoracion = base["valoracion"]
    salario = f"${base['salario_min_k']:.0f}K - ${base['salario_max_k']:.0f}K"
    val_txt = "s/d" if pd.isna(valoracion) else f"{valoracion:.1f} / 5"
    st.markdown("**Oferta seleccionada:**")
    st.caption(f"{base['puesto']} — {base['empresa']}")
    # Se pasa el valor completo tambien como 'help' (tooltip) porque el texto de
    # st.metric se recorta cuando no cabe en la columna.
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sector", base["sector"], help=base["sector"])
    c2.metric("Empresa", base["empresa"], help=base["empresa"])
    c3.metric("Salario", salario, help=salario)
    c4.metric("Valoracion", val_txt, help=val_txt)

    similitudes = cosine_similarity([matriz[idx]], matriz)[0]
    orden = np.argsort(similitudes)[::-1]
    recomendados = [i for i in orden if i != idx][:n]

    resultado = df.iloc[recomendados][_COLS_MOSTRAR].copy()
    resultado.insert(0, "Similitud", [f"{similitudes[i]*100:.1f}%" for i in recomendados])

    st.markdown(f"#### Top {n} empleos recomendados")
    st.dataframe(resultado, width="stretch", hide_index=True)


def _por_preferencias(df: pd.DataFrame):
    st.markdown("Indica tus preferencias y te recomendamos empleos que encajen.")
    c1, c2 = st.columns(2)
    with c1:
        sectores = st.multiselect("Sectores de interes", sorted(df["sector"].unique()))
        estados = st.multiselect("Estado", sorted(df["estado"].unique()))
        tamanos = st.multiselect("Tamano de empresa", sorted(df["tamano_empresa"].unique()))
    with c2:
        salario_min = st.slider("Salario promedio minimo (miles USD)", 0,
                                int(df["salario_prom_k"].max()), 60, step=5)
        valoracion_min = st.slider("Valoracion minima de empresa", 1.0, 5.0, 3.0, 0.1)
        incluir_sin_valoracion = st.checkbox(
            "Incluir empresas sin valoracion", value=False)
    n = st.slider("Cantidad de recomendaciones", 3, 15, 8)

    filtro = df.copy()
    if sectores:
        filtro = filtro[filtro["sector"].isin(sectores)]
    if estados:
        filtro = filtro[filtro["estado"].isin(estados)]
    if tamanos:
        filtro = filtro[filtro["tamano_empresa"].isin(tamanos)]
    filtro = filtro[filtro["salario_prom_k"] >= salario_min]

    # Filtro de valoracion (los NaN se conservan solo si el usuario lo pide)
    cumple_val = filtro["valoracion"] >= valoracion_min
    if incluir_sin_valoracion:
        cumple_val = cumple_val | filtro["valoracion"].isna()
    filtro = filtro[cumple_val]

    if filtro.empty:
        st.warning("Ningun empleo cumple esos criterios. Prueba a relajar los filtros.")
        return

    # Ranking: combinacion de salario y valoracion de la empresa
    filtro = filtro.copy()
    filtro["score"] = (filtro["salario_prom_k"] / df["salario_prom_k"].max() * 0.6 +
                       filtro["valoracion"].fillna(0) / 5 * 0.4)
    top = filtro.sort_values("score", ascending=False).head(n)

    st.markdown(f"#### {len(top)} empleos recomendados para ti")
    st.caption(f"{len(filtro)} empleos cumplen tus criterios.")
    st.dataframe(top[_COLS_MOSTRAR], width="stretch", hide_index=True)
