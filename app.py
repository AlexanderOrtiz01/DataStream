# -*- coding: utf-8 -*-
"""
DataStream — Aplicacion de Ciencia de Datos (Streamlit)
Tecnica Electiva I · Ciencia de Datos — Ciclo I-2026
Tarea Laboratorio I y II · Computo 3

Ejecutar:  streamlit run app.py
"""
import streamlit as st
import plotly.express as px

from secciones import (
    inicio, exploratorio, aprendizaje, recomendacion,
    carga_archivos, sentimientos, interfaz_ia,
)
from utils.estilos import aplicar_estilos

# Paleta de los graficos alineada al portafolio: el verde #08D665 encabeza la
# secuencia cualitativa (sustituye al azul/morado por defecto de Plotly) y las
# escalas continuas usan tonos de verde. Aplica a todos los px.* de la app.
px.defaults.color_discrete_sequence = [
    "#08D665", "#19D3F3", "#FFA15A", "#EF553B",
    "#B6E880", "#FF6692", "#FECB52", "#1f9e6b",
]
px.defaults.color_continuous_scale = "Greens"

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
        st.Page(interfaz_ia.mostrar, title="Interfaz IA",
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
    """Configuracion de la IA y ayuda, debajo de la navegacion."""
    with st.sidebar:
        st.divider()

        # Componente expander (layout) para la configuracion de la API key
        with st.expander("Configurar IA"):
            st.caption(
                "Para las opciones de IA (sentimientos y consultas). Introduce "
                "tu clave de API para habilitarlas.")
            clave = st.text_input("API key de IA", type="password",
                                  value=st.session_state.get("ia_api_key", ""))
            if clave:
                st.session_state["ia_api_key"] = clave
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

        st.caption("Hecho con Streamlit · scikit-learn · Plotly · IA")


_URL_PORTAFOLIO = "https://alexanderortiz01.github.io/PortfolioEdwinOrtiz/#portfolio"


def pie_portafolio():
    """Boton al final de cada pagina para volver al portafolio (seccion DataStream)."""
    st.divider()
    _, centro, _ = st.columns([1, 2, 1])
    with centro:
        st.link_button("← Regresar al portafolio", _URL_PORTAFOLIO,
                       width="stretch")


def main():
    aplicar_estilos()
    encabezado_sidebar()
    navegacion = st.navigation(PAGINAS, position="sidebar")
    configuracion_sidebar()
    navegacion.run()
    pie_portafolio()


if __name__ == "__main__":
    main()
