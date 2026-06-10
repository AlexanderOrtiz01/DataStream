# -*- coding: utf-8 -*-
"""Opcion 5: Analisis de Datos por Carga de Archivos (CSV / Excel)."""
import pandas as pd
import plotly.express as px
import streamlit as st

from utils.datos import detectar_columnas_codigo
from utils.almacen import (
    guardar_archivo, hay_archivo, obtener_df, obtener_nombre, eliminar_archivo,
)


def mostrar():
    st.title("Analisis de Datos por Carga de Archivos")
    st.write(
        "Carga un archivo **CSV** o **Excel** desde tu computadora. La aplicacion lo "
        "analiza automaticamente y genera graficos a partir de sus datos. El archivo "
        "queda **guardado** y disponible en la **Interfaz IA** hasta que lo elimines."
    )

    # Clave dinamica del uploader: al eliminar el archivo se incrementa para que el
    # widget se recree vacio (de lo contrario seguiria conservando el archivo subido).
    st.session_state.setdefault("uploader_key", 0)
    archivo = st.file_uploader(
        "Selecciona un archivo (CSV o Excel)", type=["csv", "xlsx", "xls"],
        key=f"uploader_{st.session_state['uploader_key']}")

    # 1) Si se subio un archivo nuevo, se lee y se guarda en la sesion.
    if archivo is not None:
        try:
            if archivo.name.lower().endswith(".csv"):
                sep = st.text_input("Separador del CSV", value=",")
                df = pd.read_csv(archivo, sep=sep)
            else:
                df = pd.read_excel(archivo)
        except Exception as e:  # noqa: BLE001
            st.error(f"No se pudo leer el archivo: {e}")
            return
        guardar_archivo(archivo.name, df)
        nombre = archivo.name
    # 2) Si no, pero hay uno guardado en la sesion, se reutiliza ese.
    elif hay_archivo():
        df = obtener_df()
        nombre = obtener_nombre()
    # 3) Si no hay nada, se espera un archivo.
    else:
        st.info("Esperando un archivo. Una vez cargado, quedara guardado para "
                "analizarlo aqui y consultarlo en la Interfaz IA.")
        return

    # Barra de estado del archivo + boton para eliminarlo
    col_info, col_del = st.columns([3, 1])
    with col_info:
        st.success(f"Archivo **{nombre}** cargado: "
                   f"{df.shape[0]:,} filas × {df.shape[1]} columnas.")
        st.caption("Guardado en esta sesion. Disponible en la Interfaz IA.")
    with col_del:
        if st.button("Eliminar archivo", type="secondary", width="stretch"):
            eliminar_archivo()
            st.session_state["uploader_key"] += 1  # recrea el uploader vacio
            st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Vista previa", "Resumen", "Graficos", "Buscar por codigo"])

    with tab1:
        st.dataframe(df, width="stretch")

    with tab2:
        c1, c2, c3 = st.columns(3)
        c1.metric("Filas", f"{df.shape[0]:,}")
        c2.metric("Columnas", df.shape[1])
        c3.metric("Valores nulos", int(df.isna().sum().sum()))
        st.markdown("**Tipos de datos:**")
        st.dataframe(pd.DataFrame({"Columna": df.columns,
                                   "Tipo": [str(t) for t in df.dtypes],
                                   "Nulos": df.isna().sum().values}),
                     width="stretch", hide_index=True)
        numericas = df.select_dtypes(include="number")
        if not numericas.empty:
            st.markdown("**Estadisticas (columnas numericas):**")
            st.dataframe(numericas.describe().round(2), width="stretch")

    with tab3:
        _graficos(df)

    with tab4:
        _buscar_por_codigo(df)


def _buscar_por_codigo(df: pd.DataFrame):
    candidatas = detectar_columnas_codigo(df)
    if not candidatas:
        st.info("No se detectaron columnas tipo codigo o identificador "
                "(id, cod, codigo, code, clave, sku, ...).")
        return

    st.write("Se detectaron estas columnas como posibles **codigos / "
             "identificadores**. Elige una y busca un valor para ver su ficha.")
    col = st.selectbox("Columna identificadora", candidatas)

    serie = df[col].astype(str)
    valor = st.text_input("Valor a buscar", placeholder="Escribe un codigo").strip()
    if not valor:
        return

    coincidencia = df[serie.str.strip().str.casefold() == valor.casefold()]
    if coincidencia.empty:
        st.warning(f"No se encontro ningun registro con `{col}` = '{valor}'.")
        return

    st.success(f"{len(coincidencia)} registro(s) encontrado(s).")
    registro = coincidencia.iloc[0]
    ficha = registro.to_frame(name="Valor")
    ficha.index.name = "Campo"
    st.dataframe(ficha, width="stretch")


def _graficos(df: pd.DataFrame):
    numericas = df.select_dtypes(include="number").columns.tolist()
    categoricas = df.select_dtypes(exclude="number").columns.tolist()

    tipo = st.selectbox("Tipo de grafico",
                        ["Histograma", "Barras (categorias)", "Dispersion", "Caja"])

    if tipo == "Histograma":
        if not numericas:
            st.warning("El archivo no tiene columnas numericas.")
            return
        col = st.selectbox("Columna", numericas)
        st.plotly_chart(px.histogram(df, x=col, nbins=30, marginal="box",
                                     title=f"Distribucion de {col}"),
                        width="stretch")

    elif tipo == "Barras (categorias)":
        cols = categoricas or df.columns.tolist()
        col = st.selectbox("Columna", cols)
        conteo = df[col].astype(str).value_counts().head(20).reset_index()
        conteo.columns = [col, "frecuencia"]
        st.plotly_chart(px.bar(conteo, x=col, y="frecuencia",
                               title=f"Frecuencia de {col}"),
                        width="stretch")

    elif tipo == "Dispersion":
        if len(numericas) < 2:
            st.warning("Se necesitan al menos dos columnas numericas.")
            return
        c1, c2 = st.columns(2)
        x = c1.selectbox("Eje X", numericas, index=0)
        y = c2.selectbox("Eje Y", numericas, index=1)
        color = st.selectbox("Color (opcional)", ["(ninguno)"] + categoricas)
        kwargs = {} if color == "(ninguno)" else {"color": color}
        st.plotly_chart(px.scatter(df, x=x, y=y, title=f"{x} vs {y}", **kwargs),
                        width="stretch")

    elif tipo == "Caja":
        if not numericas:
            st.warning("El archivo no tiene columnas numericas.")
            return
        y = st.selectbox("Columna numerica", numericas)
        x = st.selectbox("Agrupar por (opcional)", ["(ninguno)"] + categoricas)
        kwargs = {} if x == "(ninguno)" else {"x": x}
        st.plotly_chart(px.box(df, y=y, title=f"Diagrama de caja de {y}", **kwargs),
                        width="stretch")
