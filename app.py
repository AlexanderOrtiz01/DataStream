# -*- coding: utf-8 -*-
"""
DataStream — Aplicacion de Ciencia de Datos (Streamlit)
Tecnica Electiva I · Ciencia de Datos — Ciclo I-2026
Tarea Laboratorio I y II · Computo 3

Ejecutar:  streamlit run app.py
"""
import streamlit as st

from secciones import (
    inicio, exploratorio, aprendizaje, recomendacion,
    carga_archivos, sentimientos, interfaz_ia,
)
from utils.estilos import aplicar_estilos

st.set_page_config(
    page_title="DataStream · Ciencia de Datos",
    page_icon=":material/work:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Definicion de las paginas, agrupadas en secciones. st.navigation las muestra
# como las opciones de la barra de navegacion (sidebar), agrupadas por tarea.
PAGINAS = {
    "Inicio": [
        st.Page(inicio.mostrar, title="Inicio", icon=":material/home:",
                url_path="inicio", default=True),
    ],
    "Tarea 1 · Laboratorio I": [
        st.Page(exploratorio.mostrar, title="Analisis Exploratorio",
                icon=":material/analytics:", url_path="exploratorio"),
        st.Page(aprendizaje.mostrar, title="Aprendizaje Automatico",
                icon=":material/smart_toy:", url_path="aprendizaje"),
        st.Page(recomendacion.mostrar, title="Sistema de Recomendacion",
                icon=":material/recommend:", url_path="recomendacion"),
    ],
    "Tarea 2 · Laboratorio II": [
        st.Page(carga_archivos.mostrar, title="Carga de Archivos",
                icon=":material/upload_file:", url_path="carga-archivos"),
        st.Page(sentimientos.mostrar, title="Sentimientos y Scraping",
                icon=":material/reviews:", url_path="sentimientos"),
        st.Page(interfaz_ia.mostrar, title="Interfaz IA (Gemini)",
                icon=":material/auto_awesome:", url_path="interfaz-ia"),
    ],
}


def encabezado_sidebar():
    """Marca/identidad de la app, en la parte superior del sidebar."""
    with st.sidebar:
        with st.container():
            st.markdown("## DataStream")
            st.caption("Ciencia de Datos · Ciclo I-2026")


def configuracion_sidebar():
    """Configuracion de Gemini y ayuda, debajo de la navegacion."""
    with st.sidebar:
        st.divider()

        # Componente expander (layout) para la configuracion de la API key
        with st.expander("Configurar Gemini (IA)"):
            st.caption(
                "Para las opciones de IA (sentimientos y consultas). Obten una "
                "clave gratuita en aistudio.google.com/app/apikey.")
            clave = st.text_input("API key de Gemini", type="password",
                                  value=st.session_state.get("gemini_api_key", ""))
            if clave:
                st.session_state["gemini_api_key"] = clave
                st.success("Clave guardada para esta sesion.")

        # Componente popover (layout) con informacion del proyecto
        with st.popover("Acerca de esta app"):
            st.markdown(
                "**DataStream** integra un flujo completo de Ciencia de Datos sobre "
                "un dataset real de **empleos de Data Analyst** (Glassdoor).\n\n"
                "- **Tarea 1:** analisis exploratorio, aprendizaje automatico, "
                "sistema de recomendacion y pregunta IA.\n"
                "- **Tarea 2:** carga de archivos, analisis de sentimientos con "
                "scraping e interfaz IA.\n\n"
                "**Fuente del dataset:** "
                "[Data Analyst Jobs (Kaggle)]"
                "(https://www.kaggle.com/datasets/andrewmvd/data-analyst-jobs)")

        st.caption("Hecho con Streamlit · scikit-learn · Plotly · Gemini")


def main():
    aplicar_estilos()
    encabezado_sidebar()
    navegacion = st.navigation(PAGINAS, position="sidebar")
    configuracion_sidebar()
    navegacion.run()


if __name__ == "__main__":
    main()
