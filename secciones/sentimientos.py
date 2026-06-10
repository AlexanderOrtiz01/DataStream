# -*- coding: utf-8 -*-
"""Opcion 6: Analisis de Sentimientos y Web Scraping."""
import pandas as pd
import plotly.express as px
import streamlit as st

from utils.scraping import scrape_url, OPINIONES_DEMO
from utils.sentimiento import analizar_lexico, analizar_ia
from utils.filtro_opiniones import filtrar_comentarios
from utils.ia import hay_api_key

_COLORES = {"Positivo": "#2ca02c", "Negativo": "#d62728", "Neutral": "#7f7f7f"}


def mostrar():
    st.title("Analisis de Sentimientos y Scraping")
    st.write(
        "Lee opiniones desde un sitio web (web scraping) o usa el conjunto de "
        "opiniones de demostracion, y realiza un **analisis de sentimientos** sobre "
        "ellas."
    )

    # ----------------------------- Fuente de datos ------------------------ #
    st.subheader("1 · Origen de las opiniones")
    fuente = st.radio(
        "Selecciona la fuente",
        ["Opiniones de demostracion (resenas de empleos)",
         "Web scraping de una URL",
         "Pegar texto manualmente"],
    )

    opiniones = []
    if fuente.startswith("Opiniones de demostracion"):
        opiniones = OPINIONES_DEMO
        st.caption(f"{len(opiniones)} opiniones de demostracion cargadas.")

    elif fuente.startswith("Web scraping"):
        url = st.text_input("URL del sitio (foro, noticias, red social, etc.)",
                            placeholder="https://...")
        if st.button("Leer opiniones de la URL", type="primary"):
            if not url:
                st.warning("Ingresa una URL valida.")
            else:
                try:
                    with st.spinner("Descargando y extrayendo opiniones..."):
                        opiniones = scrape_url(url)
                    if opiniones:
                        st.session_state["opiniones_scrape"] = opiniones
                        st.success(f"Se extrajeron {len(opiniones)} fragmentos de texto.")
                    else:
                        st.warning("No se encontraron textos con aspecto de opinion.")
                except Exception as e:  # noqa: BLE001
                    st.error(f"No se pudo leer la URL: {e}")
        opiniones = st.session_state.get("opiniones_scrape", opiniones)

    else:
        texto = st.text_area(
            "Escribe una opinion por linea",
            value="\n".join(OPINIONES_DEMO[:5]), height=160)
        opiniones = [l.strip() for l in texto.splitlines() if l.strip()]

    if not opiniones:
        st.info("Aun no hay opiniones para analizar.")
        return

    # --------------------------- Filtro de opiniones ---------------------- #
    # Detecta y conserva solo los fragmentos que parecen un comentario u opinion
    # real, descartando ruido web (menus, fechas, URLs, cookies, titulares...).
    filtrar = st.toggle(
        "Detectar y analizar solo comentarios/opiniones reales", value=True,
        help="Descarta texto que no parece un comentario: menus, fechas, enlaces, "
             "avisos de cookies/login, titulares sueltos, numeros, etc.")

    descartadas = []
    if filtrar:
        with st.spinner("Detectando comentarios..."):
            resultado = filtrar_comentarios(opiniones)
        opiniones, descartadas = resultado["opiniones"], resultado["descartadas"]

    if not opiniones:
        st.warning("Tras el filtrado no quedo ningun comentario valido. "
                   "Desactiva el filtro o usa otra fuente.")
        return

    # ----------------------------- Motor ---------------------------------- #
    st.subheader("2 · Opiniones leidas")
    if filtrar:
        st.caption(f"Se conservaron **{len(opiniones)}** comentarios y se "
                   f"descartaron **{len(descartadas)}** fragmentos que no parecian "
                   f"opiniones.")
    st.dataframe(pd.DataFrame({"Opinion": opiniones}),
                 width="stretch", hide_index=True)

    if descartadas:
        with st.expander(f"Ver {len(descartadas)} fragmentos descartados y el motivo"):
            st.dataframe(
                pd.DataFrame(descartadas, columns=["Texto descartado", "Motivo"]),
                width="stretch", hide_index=True)

    st.subheader("3 · Analisis de sentimientos")
    opciones_motor = ["Lexico en espaniol (sin conexion)"]
    if hay_api_key():
        opciones_motor.insert(0, "IA (mas preciso)")
    motor = st.selectbox("Motor de analisis", opciones_motor)

    if not st.button("Analizar sentimientos", type="primary"):
        return

    if motor.startswith("IA"):
        try:
            with st.spinner("Consultando a la IA..."):
                etiquetas = analizar_ia(opiniones)
            puntajes = [None] * len(opiniones)
        except Exception as e:  # noqa: BLE001
            st.warning(f"Fallo la IA ({e}). Se usa el analizador lexico.")
            resultados = [analizar_lexico(o) for o in opiniones]
            etiquetas = [r["sentimiento"] for r in resultados]
            puntajes = [r["puntaje"] for r in resultados]
    else:
        resultados = [analizar_lexico(o) for o in opiniones]
        etiquetas = [r["sentimiento"] for r in resultados]
        puntajes = [r["puntaje"] for r in resultados]

    tabla = pd.DataFrame({
        "Opinion": opiniones,
        "Sentimiento": etiquetas,
        "Puntaje": puntajes,
    })

    st.markdown("**Resultados:**")
    st.dataframe(tabla, width="stretch", hide_index=True)

    # ----------------------------- Resumen -------------------------------- #
    st.subheader("4 · Resumen")
    conteo = tabla["Sentimiento"].value_counts().reset_index()
    conteo.columns = ["Sentimiento", "Cantidad"]

    c1, c2, c3 = st.columns(3)
    total = len(tabla)
    pos = int((tabla["Sentimiento"] == "Positivo").sum())
    neg = int((tabla["Sentimiento"] == "Negativo").sum())
    neu = int((tabla["Sentimiento"] == "Neutral").sum())
    c1.metric("Positivas", pos, f"{pos/total*100:.0f}%")
    c2.metric("Negativas", neg, f"{neg/total*100:.0f}%")
    c3.metric("Neutrales", neu, f"{neu/total*100:.0f}%")

    col_a, col_b = st.columns(2)
    with col_a:
        fig = px.bar(conteo, x="Sentimiento", y="Cantidad", color="Sentimiento",
                     color_discrete_map=_COLORES, title="Distribucion de sentimientos")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")
    with col_b:
        fig2 = px.pie(conteo, names="Sentimiento", values="Cantidad",
                      color="Sentimiento", color_discrete_map=_COLORES,
                      title="Proporcion de sentimientos")
        st.plotly_chart(fig2, width="stretch")

    if pos > neg:
        st.success("**Conclusion:** predominan las opiniones **positivas**.")
    elif neg > pos:
        st.error("**Conclusion:** predominan las opiniones **negativas**.")
    else:
        st.info("**Conclusion:** las opiniones estan **equilibradas**.")
