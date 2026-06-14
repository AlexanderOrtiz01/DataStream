# -*- coding: utf-8 -*-
"""Opcion 2: Analisis Exploratorio (con submenus)."""
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy import stats

from utils.datos import (
    cargar_datos, columnas_numericas, columnas_categoricas,
    descripcion_de, COLUMNA_CODIGO, DESCRIPCIONES,
)


def mostrar():
    st.title("Analisis Exploratorio")
    df = cargar_datos()

    tabs = st.tabs([
        "Descripcion del dataset",
        "Descripcion de campos",
        "Navegador",
        "Buscador por codigo",
        "Graficador",
        "Hipotesis",
    ])

    with tabs[0]:
        _descripcion_dataset(df)
    with tabs[1]:
        _descripcion_campos(df)
    with tabs[2]:
        _navegador(df)
    with tabs[3]:
        _buscador(df)
    with tabs[4]:
        _graficador(df)
    with tabs[5]:
        _hipotesis(df)


# Estadisticas de describe(): nombre legible en espaniol + ayuda (tooltip).
_DESCRIBE_INFO = {
    "count": ("Conteo", "Cantidad de valores no nulos del campo."),
    "mean": ("Media", "Promedio aritmetico de todos los valores."),
    "std": ("Desv. tipica", "Desviacion estandar: que tanto se dispersan los "
                            "valores respecto a la media."),
    "min": ("Minimo", "Valor mas pequeno del campo."),
    "25%": ("P25", "Percentil 25: el 25% de los datos esta por debajo de este valor."),
    "50%": ("Mediana", "Percentil 50 (mediana): la mitad de los datos esta por "
                       "debajo de este valor."),
    "75%": ("P75", "Percentil 75: el 75% de los datos esta por debajo de este valor."),
    "max": ("Maximo", "Valor mas grande del campo."),
}


def _tabla_describe(desc_df: pd.DataFrame, hide_index: bool = False):
    """Muestra una tabla de describe() con nombres en espaniol y tooltips.

    Recibe el DataFrame tal como lo devuelve describe() (estadisticas en el
    indice). Lo transpone para que las estadisticas sean columnas (asi Streamlit
    puede mostrar la ayuda al pasar el cursor por la cabecera).
    """
    tabla = desc_df.T.rename(columns={k: v[0] for k, v in _DESCRIBE_INFO.items()})
    ayudas = {v[0]: v[1] for v in _DESCRIBE_INFO.values()}
    config = {col: st.column_config.NumberColumn(col, help=ayudas.get(col))
              for col in tabla.columns}
    st.dataframe(tabla, width="stretch", column_config=config, hide_index=hide_index)


# --------------------------------------------------------------------------- #
def _descripcion_dataset(df: pd.DataFrame):
    st.subheader("Descripcion del dataset")
    st.write(
        "El dataset reune **ofertas de empleo de Data Analyst** publicadas en "
        "Glassdoor: el puesto, la empresa que lo publica y su valoracion, datos de "
        "la empresa (sector, industria, tamano, ingresos, antiguedad, sede) y el "
        "salario anual estimado (rango en miles de USD). Permite estudiar que "
        "factores de la empresa se relacionan con el salario ofrecido. Los datos se "
        "limpiaron desde el archivo original (salario en texto, valores faltantes "
        "marcados como -1, etc.)."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Numero de registros", f"{df.shape[0]:,}")
    c2.metric("Numero de campos", df.shape[1])
    c3.metric("Valores nulos", int(df.isna().sum().sum()))

    st.markdown("**Tipos de datos por campo:**")
    info = pd.DataFrame({
        "Campo": df.columns,
        "Tipo": [str(t) for t in df.dtypes],
        "No nulos": df.notna().sum().values,
        "Valores unicos": [df[c].nunique() for c in df.columns],
    })
    st.dataframe(info, width="stretch", hide_index=True)

    st.markdown("**Estadisticas generales (campos numericos):**")
    st.caption("Pasa el cursor por la cabecera de cada columna para ver que "
               "significa la estadistica.")
    _tabla_describe(df.describe().round(2))


# --------------------------------------------------------------------------- #
def _descripcion_campos(df: pd.DataFrame):
    st.subheader("Descripcion de los campos")
    st.write("Selecciona un campo para ver su descripcion y sus medidas.")

    campo = st.selectbox("Campo", df.columns.tolist())
    st.info(f"**{campo}** — {descripcion_de(campo)}")

    es_numerico = pd.api.types.is_numeric_dtype(df[campo]) and campo != COLUMNA_CODIGO

    if es_numerico:
        st.markdown("**Campo cuantitativo — medidas estadisticas:**")
        desc = df[campo].describe()
        ayuda = {k: v[1] for k, v in _DESCRIBE_INFO.items()}
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Media", f"{desc['mean']:.2f}", help=ayuda["mean"])
        c2.metric("Desv. tipica", f"{desc['std']:.2f}", help=ayuda["std"])
        c3.metric("Minimo", f"{desc['min']:.2f}", help=ayuda["min"])
        c4.metric("Maximo", f"{desc['max']:.2f}", help=ayuda["max"])
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Percentil 25", f"{desc['25%']:.2f}", help=ayuda["25%"])
        c2.metric("Mediana", f"{desc['50%']:.2f}", help=ayuda["50%"])
        c3.metric("Percentil 75", f"{desc['75%']:.2f}", help=ayuda["75%"])
        c4.metric("Conteo", f"{int(desc['count'])}", help=ayuda["count"])
        _tabla_describe(desc.round(3).to_frame(name=campo))
    else:
        st.markdown("**Campo categorico — posibles valores:**")
        conteo = df[campo].value_counts().reset_index()
        conteo.columns = [campo, "frecuencia"]
        conteo["porcentaje"] = (conteo["frecuencia"] / len(df) * 100).round(2)
        st.write(f"Cantidad de valores distintos: **{df[campo].nunique()}**")
        st.dataframe(conteo, width="stretch", hide_index=True)


# --------------------------------------------------------------------------- #
def _navegador(df: pd.DataFrame):
    st.subheader("Navegador del dataset completo")
    st.write("Explora, filtra y ordena todos los registros del dataset.")

    c1, c2 = st.columns(2)
    with c1:
        sectores = st.multiselect(
            "Filtrar por sector", sorted(df["sector"].unique()))
    with c2:
        estados = st.multiselect(
            "Filtrar por estado", sorted(df["estado"].unique()))

    filtrado = df.copy()
    if sectores:
        filtrado = filtrado[filtrado["sector"].isin(sectores)]
    if estados:
        filtrado = filtrado[filtrado["estado"].isin(estados)]

    orden = st.selectbox("Ordenar por", df.columns.tolist(),
                         index=df.columns.get_loc("salario_prom_k"))
    ascendente = st.toggle("Orden ascendente", value=False)
    filtrado = filtrado.sort_values(orden, ascending=ascendente)

    st.caption(f"Mostrando {len(filtrado):,} de {len(df):,} registros.")
    st.dataframe(filtrado, width="stretch", hide_index=True)

    st.download_button(
        "Descargar resultado (CSV)",
        filtrado.to_csv(index=False).encode("utf-8"),
        "empleos_filtrado.csv", "text/csv",
    )


# --------------------------------------------------------------------------- #
def _buscador(df: pd.DataFrame):
    st.subheader("Buscador de registros por codigo  ·  Bonus")
    st.write("Ingresa un codigo de oferta (ej. `DA0001`) para ver su ficha.")

    codigos = df[COLUMNA_CODIGO].tolist()
    modo = st.radio("Modo de busqueda", ["Escribir codigo", "Elegir de la lista"],
                    horizontal=True)
    if modo == "Escribir codigo":
        valor = st.text_input("Codigo", placeholder="DA0001").strip().upper()
    else:
        valor = st.selectbox("Codigo", codigos)

    if not valor:
        return

    coincidencia = df[df[COLUMNA_CODIGO].str.upper() == valor]
    if coincidencia.empty:
        st.warning(f"No se encontro ningun registro con el codigo '{valor}'.")
        return

    registro = coincidencia.iloc[0]
    st.success(f"Registro encontrado: **{registro['puesto']}** — {registro['empresa']}")
    valoracion = registro["valoracion"]
    salario = f"${registro['salario_min_k']:.0f}K - ${registro['salario_max_k']:.0f}K"
    val_txt = "s/d" if pd.isna(valoracion) else f"{valoracion:.1f} / 5"
    ubicacion = f"{registro['ciudad']}, {registro['estado']}"
    # El valor completo va tambien como 'help' (tooltip): st.metric recorta el
    # texto cuando no cabe en la columna.
    c1, c2, c3 = st.columns(3)
    c1.metric("Salario estimado", salario, help=salario)
    c2.metric("Valoracion empresa", val_txt, help=val_txt)
    c3.metric("Ubicacion", ubicacion, help=ubicacion)

    # La ficha mezcla textos, numeros y nulos en una sola columna: se convierte a
    # texto para una visualizacion homogenea (evita avisos de serializacion Arrow).
    ficha = registro.astype(str).to_frame(name="Valor")
    ficha.index.name = "Campo"
    st.dataframe(ficha, width="stretch")


# --------------------------------------------------------------------------- #
def _graficador(df: pd.DataFrame):
    st.subheader("Graficador exploratorio")
    st.write(
        "Selecciona un campo y la aplicacion elige automaticamente el grafico "
        "mas adecuado segun su tipo de dato."
    )

    campo = st.selectbox("Campo a graficar",
                         columnas_numericas(df) + columnas_categoricas(df))
    es_numerico = pd.api.types.is_numeric_dtype(df[campo])

    if es_numerico:
        st.caption(f"`{campo}` es **cuantitativo**: histograma + diagrama de caja.")
        fig = px.histogram(df, x=campo, nbins=30, marginal="box",
                           title=f"Distribucion de {campo}",
                           color_discrete_sequence=["#08D665"])
        st.plotly_chart(fig, width="stretch")
    else:
        st.caption(f"`{campo}` es **categorico**: grafico de barras de frecuencias.")
        conteo = df[campo].value_counts().reset_index()
        conteo.columns = [campo, "frecuencia"]
        fig = px.bar(conteo, x=campo, y="frecuencia", color=campo,
                     title=f"Frecuencia de {campo}")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")

        fig2 = px.pie(conteo, names=campo, values="frecuencia",
                      title=f"Proporcion de {campo}")
        st.plotly_chart(fig2, width="stretch")


# --------------------------------------------------------------------------- #
def _hipotesis(df: pd.DataFrame):
    st.subheader("Validacion de hipotesis")
    st.write("Selecciona una hipotesis para ver su analisis y conclusion.")

    hipotesis = st.selectbox("Hipotesis", [
        "H1: Las empresas mejor valoradas ofrecen mayor salario.",
        "H2: El sector economico influye en el salario ofrecido.",
        "H3: Las ofertas con 'Easy Apply' ofrecen un salario distinto.",
    ])

    st.divider()

    if hipotesis.startswith("H1"):
        _hipotesis_valoracion(df)
    elif hipotesis.startswith("H2"):
        _hipotesis_sector(df)
    else:
        _hipotesis_easyapply(df)


def _hipotesis_valoracion(df: pd.DataFrame):
    st.markdown("#### H1 · Valoracion de la empresa vs salario")
    datos = df[["valoracion", "salario_prom_k"]].dropna()
    r, p = stats.pearsonr(datos["valoracion"], datos["salario_prom_k"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Correlacion de Pearson (r)", f"{r:.3f}")
    c2.metric("Valor p", f"{p:.4g}", help=_ayuda_p(p))
    c3.metric("Ofertas analizadas", f"{len(datos):,}")

    fig = px.scatter(datos, x="valoracion", y="salario_prom_k",
                     trendline="ols", opacity=0.5,
                     title="Relacion entre valoracion de la empresa y salario",
                     labels={"valoracion": "Valoracion (1-5)",
                             "salario_prom_k": "Salario promedio (miles USD)"},
                     color_discrete_sequence=["#9aa7b3"],
                     trendline_color_override="#08D665")
    st.plotly_chart(fig, width="stretch")

    valida = (p < 0.05) and (r > 0.1)
    fuerza = ("debil" if abs(r) < 0.3 else "moderada" if abs(r) < 0.6 else "fuerte")
    _conclusion(
        valida,
        f"Existe una correlacion positiva **{fuerza}** (r = {r:.3f}, p < 0.05) entre "
        f"la valoracion de la empresa y el salario ofrecido: las empresas mejor "
        f"valoradas tienden a pagar mas. **Se valida la hipotesis.**",
        f"La correlacion observada (r = {r:.3f}, p = {p:.4g}) no respalda una "
        f"relacion positiva clara entre valoracion y salario. "
        f"**No se valida la hipotesis.**",
    )


def _hipotesis_sector(df: pd.DataFrame):
    st.markdown("#### H2 · Sector economico vs salario")
    # Solo sectores con suficientes ofertas para que el ANOVA sea fiable
    conteo = df["sector"].value_counts()
    validos = conteo[conteo >= 10].index
    datos = df[df["sector"].isin(validos)]
    medias = datos.groupby("sector")["salario_prom_k"].mean().sort_values(ascending=False)
    grupos = [g["salario_prom_k"].dropna().values for _, g in datos.groupby("sector")]
    f_stat, p = stats.f_oneway(*grupos)

    c1, c2, c3 = st.columns(3)
    c1.metric("Mejor pagado", f"{medias.index[0]}", f"${medias.iloc[0]:,.1f}K")
    c2.metric("Peor pagado", f"{medias.index[-1]}", f"${medias.iloc[-1]:,.1f}K")
    c3.metric("Valor p (ANOVA)", f"{p:.4g}", help=_ayuda_p(p))

    fig = px.box(datos, x="sector", y="salario_prom_k", color="sector",
                 title="Salario por sector economico",
                 labels={"sector": "Sector", "salario_prom_k": "Salario (miles USD)"})
    fig.update_layout(showlegend=False, xaxis={"categoryorder": "median descending"})
    st.plotly_chart(fig, width="stretch")

    valida = p < 0.05
    _conclusion(
        valida,
        f"El analisis de varianza (ANOVA) indica diferencias significativas de salario "
        f"entre sectores (p = {p:.4g} < 0.05). Sectores como **{medias.index[0]}** "
        f"pagan mas que **{medias.index[-1]}**. **Se valida la hipotesis.**",
        f"No hay evidencia de diferencias significativas de salario entre sectores "
        f"(p = {p:.4g}). **No se valida la hipotesis.**",
    )


def _hipotesis_easyapply(df: pd.DataFrame):
    st.markdown("#### H3 · 'Easy Apply' vs salario")
    medias = df.groupby("aplicacion_facil")["salario_prom_k"].mean()
    con = df[df["aplicacion_facil"] == "Si"]["salario_prom_k"].dropna()
    sin = df[df["aplicacion_facil"] == "No"]["salario_prom_k"].dropna()
    t, p = stats.ttest_ind(con, sin, equal_var=False)

    c1, c2, c3 = st.columns(3)
    c1.metric("Salario medio · Easy Apply", f"${medias.get('Si', 0):,.1f}K")
    c2.metric("Salario medio · Normal", f"${medias.get('No', 0):,.1f}K")
    c3.metric("Valor p (t-test)", f"{p:.4g}", help=_ayuda_p(p))

    fig = px.box(df, x="aplicacion_facil", y="salario_prom_k", color="aplicacion_facil",
                 title="Salario segun tipo de postulacion",
                 labels={"aplicacion_facil": "Easy Apply",
                         "salario_prom_k": "Salario (miles USD)"})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")

    diferencia = medias.get("Si", 0) - medias.get("No", 0)
    valida = p < 0.05
    _conclusion(
        valida,
        f"Las ofertas con 'Easy Apply' difieren en promedio **${diferencia:,.1f}K** "
        f"respecto a las normales, y la diferencia es estadisticamente significativa "
        f"(p = {p:.4g} < 0.05). **Se valida la hipotesis.**",
        f"La diferencia de medias (${diferencia:,.1f}K) no es estadisticamente "
        f"significativa (p = {p:.4g}). **No se valida la hipotesis.**",
    )


def _ayuda_p(p: float) -> str:
    """Tooltip con el valor exacto del p-value, sin notacion cientifica."""
    if p <= 0 or p < 1e-15:
        return "Valor exacto: practicamente cero (extremadamente significativo)."
    return f"Valor exacto: {np.format_float_positional(p, trim='-')}"


def _conclusion(valida: bool, texto_valida: str, texto_no_valida: str):
    st.markdown("##### Conclusion del analisis")
    if valida:
        st.success(texto_valida)
    else:
        st.error(texto_no_valida)
