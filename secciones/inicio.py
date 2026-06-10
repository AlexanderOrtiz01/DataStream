# -*- coding: utf-8 -*-
"""Opcion 1: Inicio."""
import streamlit as st
from utils.datos import cargar_datos


def mostrar():
    st.title("DataStream — Analisis de Empleos de Data Analyst")
    st.markdown(
        "**Tecnica Electiva I · Ciencia de Datos — Ciclo I-2026**  \n"
        "Tarea Laboratorio I y II · Computo 3"
    )
    st.divider()

    df = cargar_datos()

    st.subheader("Bienvenido")
    st.write(
        "Esta aplicacion, construida con **Streamlit**, integra un flujo completo "
        "de Ciencia de Datos sobre un conjunto de datos real de **ofertas de empleo "
        "de Data Analyst** publicadas en Glassdoor: desde el analisis exploratorio "
        "hasta el aprendizaje automatico, un sistema de recomendacion de empleos, "
        "analisis de archivos externos, analisis de sentimientos con web scraping y "
        "una interfaz de Inteligencia Artificial."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ofertas", f"{len(df):,}")
    c2.metric("Campos", df.shape[1])
    c3.metric("Sectores", df["sector"].nunique())
    c4.metric("Empresas", df["empresa"].nunique())

    st.divider()
    st.subheader("Contenido de la aplicacion")
    st.markdown(
        """
| Opcion | Seccion | Descripcion |
|---|---|---|
| 1 | **Inicio** | Presentacion general del proyecto. |
| 2 | **Analisis Exploratorio** | Descripcion del dataset y de campos, navegador, buscador, graficador e hipotesis. |
| 3 | **Aprendizaje Automatico** | Entrenamiento interactivo de modelos de regresion y clasificacion. |
| 4 | **Sistema de Recomendacion** | Recomendador de empleos basado en contenido. |
| 5 | **Carga de Archivos** | Analisis y graficos de archivos CSV/Excel del usuario. |
| 6 | **Sentimientos y Scraping** | Lectura de opiniones de la web y analisis de sentimientos. |
| 7 | **Interfaz IA** | Consultas en lenguaje natural sobre el dataset. |
        """
    )

    st.info(
        "Usa la barra de navegacion de la izquierda para moverte entre las "
        "distintas secciones."
    )

    with st.expander("Ver una muestra del dataset"):
        st.dataframe(df.head(10), width="stretch")
