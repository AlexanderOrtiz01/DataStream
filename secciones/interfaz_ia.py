# -*- coding: utf-8 -*-
"""Opcion 7: Interfaz de IA / Pregunta (consultas sobre el dataset)."""
import re
import unicodedata
import pandas as pd
import streamlit as st

from utils.datos import cargar_datos, descripcion_de
from utils.ia import preguntar_ia, hay_api_key
from utils.almacen import hay_archivo, obtener_df, obtener_nombre


# CSS especifico de esta seccion: saludo centrado con degradado (tonos de la app),
# al estilo del estado inicial de un asistente de chat. Usan st.chat_message.
_CSS_IA = """
<style>
.ia-hero { text-align: center; margin: 6vh 0 1.2rem; }
.ia-hero .ia-greeting {
  font-size: 2.3rem; font-weight: 600; line-height: 1.2; margin: 0;
  letter-spacing: -0.3px;
  background: linear-gradient(90deg, var(--ds-primary), var(--ds-cyan));
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.ia-hero .ia-sub {
  color: var(--ds-muted); font-size: 1rem; margin: 0.6rem 0 0;
}

/* Usuario: burbuja COMPACTA pegada a la derecha, sin avatar (estilo chat). */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
[data-testid="stChatMessageAvatarUser"] {
  display: none;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
[data-testid="stChatMessageContent"] {
  flex: 0 1 auto !important;          /* que NO crezca a todo el ancho */
  width: fit-content; max-width: 75%;
  margin-left: auto; margin-right: 3rem;   /* separada del borde derecho */
  background: var(--ds-primary-soft);
  border-radius: 18px; padding: 0.4rem 1rem;
}
/* IA: texto plano a la izquierda, sin avatar (estilo chat). */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"])
[data-testid="stChatMessageAvatarAssistant"] {
  display: none;
}

/* Boton "Limpiar" (escoba) junto al de enviar: mismo look que el de enviar del
   chat (icono morado, sin relleno, redondo, hover suave). */
[data-testid="stMain"] .stButton > button[data-testid="stBaseButton-tertiary"] {
  background: transparent !important; box-shadow: none !important;
  border: none !important; border-radius: 50% !important;
  padding: 0.45rem !important; min-height: 0 !important;
  color: var(--ds-primary) !important;
}
[data-testid="stMain"] .stButton > button[data-testid="stBaseButton-tertiary"]:hover {
  background: var(--ds-primary-soft) !important;
  color: var(--ds-primary-600) !important;
}
[data-testid="stMain"] .stButton > button[data-testid="stBaseButton-tertiary"] span,
[data-testid="stMain"] .stButton
> button[data-testid="stBaseButton-tertiary"] [data-testid="stIconMaterial"] {
  color: var(--ds-primary) !important;
}

/* El contenedor del input FLOTA pegado al fondo y permanece ahi al hacer scroll
   (position: sticky respeta el ancho del area principal y no se mete bajo el
   sidebar). El fondo tapa los mensajes que pasan por detras al desplazarse.
   Sticky tambien sirve de ancla para colocar la escoba en absoluto. */
.st-key-ia_input_box {
  position: sticky; bottom: 0; z-index: 50;
  background: var(--ds-bg); padding-top: 0.6rem;
}
.st-key-ia_input_box [data-testid="stChatInput"] textarea {
  padding-right: 5.5rem !important;   /* deja sitio para escoba + enviar */
}
.st-key-btn_limpiar {
  position: absolute; right: 3.1rem; bottom: 0.35rem; z-index: 5;
  width: auto !important; min-width: 0 !important; margin: 0 !important;
}
.st-key-btn_limpiar [data-testid="stBaseButton-tertiary"] { padding: 0.3rem !important; }
</style>
"""


def mostrar():
    st.markdown(_CSS_IA, unsafe_allow_html=True)

    # Historial de la conversacion: se conserva en la sesion y va creciendo.
    st.session_state.setdefault("ia_historial", [])

    # Fuentes de datos: el dataset principal y, si existe, el archivo cargado.
    fuentes = {"Dataset principal (Data Analyst)": "principal"}
    if hay_archivo():
        fuentes[f"Archivo cargado: {obtener_nombre()}"] = "archivo"

    # Controles superiores: fuente de datos e IA. La seleccion se guarda en la
    # sesion (key="ia_fuente") para que se mantenga entre preguntas y navegacion.
    opciones = list(fuentes.keys())
    if st.session_state.get("ia_fuente") not in opciones:
        st.session_state["ia_fuente"] = opciones[0]  # reconcilia si cambian las fuentes

    col_src, col_ia = st.columns([3, 2])
    with col_src:
        if len(opciones) > 1:
            etiqueta = st.selectbox("Datos a consultar", opciones, key="ia_fuente")
        else:
            etiqueta = st.session_state["ia_fuente"]
    with col_ia:
        usar_ia = (st.toggle("Usar IA", value=True)
                   if hay_api_key() else False)

    if not hay_api_key():
        st.caption("Sin clave de IA: respuestas con el motor interno. Agregala "
                   "en la barra lateral para respuestas flexibles y leer los registros.")

    # DataFrame segun la fuente elegida.
    df = obtener_df() if fuentes[etiqueta] == "archivo" else cargar_datos()

    # Saludo (estado inicial), solo mientras no haya conversacion.
    if not st.session_state["ia_historial"]:
        st.markdown(
            '<div class="ia-hero">'
            '<h1 class="ia-greeting">Preguntale a tus datos</h1>'
            '<p class="ia-sub">Escribe en lenguaje natural una consulta sobre los '
            'datos seleccionados. La conversacion se conserva.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    # Mensajes (se acumulan y hacen scroll).
    for msg in st.session_state["ia_historial"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Campo de entrada con el boton de limpiar (escoba) DENTRO del recuadro, a la
    # izquierda del boton de enviar. El contenedor sirve de ancla para colocar la
    # escoba en posicion absoluta sobre el campo (ver CSS .st-key-ia_input_box).
    with st.container(key="ia_input_box"):
        pregunta = st.chat_input("Pregunta sobre los datos y pulsa Enter...")
        limpiar = st.button("", icon=":material/cleaning_services:",
                            type="tertiary", key="btn_limpiar",
                            help="Limpiar la conversacion")

    if limpiar:
        st.session_state["ia_historial"] = []
        st.rerun()

    if not (pregunta and pregunta.strip()):
        return

    # Nueva pregunta: se guarda, se genera la respuesta y se recarga para que los
    # mensajes aparezcan arriba (el campo de entrada queda abajo).
    st.session_state["ia_historial"].append({"role": "user", "content": pregunta})
    respuesta = None
    if usar_ia:
        try:
            with st.spinner("Generando respuesta..."):
                respuesta = _responder_con_ia(df, pregunta)
        except Exception as e:  # noqa: BLE001
            respuesta = (_responder_local(df, pregunta)
                         + f"\n\n*(No se pudo usar la IA: {e})*")
    if respuesta is None:
        respuesta = _responder_local(df, pregunta)
    st.session_state["ia_historial"].append({"role": "assistant", "content": respuesta})
    st.rerun()


# --------------------------------------------------------------------------- #
# Presupuesto de caracteres para los registros que se envian al modelo. Limita
# el tamano del prompt (y el coste) sin dejar de incluir los datos reales.
_MAX_CHARS_DATOS = 200_000


def _muestra_csv(df: pd.DataFrame):
    """Registros en CSV, acotados a un presupuesto de caracteres.

    Devuelve (csv, n_filas_incluidas, truncado).
    """
    csv = df.to_csv(index=False)
    if len(csv) <= _MAX_CHARS_DATOS:
        return csv, len(df), False
    # Reduce el numero de filas proporcionalmente para caber en el presupuesto.
    filas = max(10, int(len(df) * _MAX_CHARS_DATOS / len(csv)))
    return df.head(filas).to_csv(index=False), filas, True


def _contexto(df: pd.DataFrame):
    """Contexto del dataset para el modelo: columnas, estadisticas y registros."""
    lineas = [f"El dataset tiene {df.shape[0]} filas y {df.shape[1]} columnas.",
              "Columnas (nombre, tipo y descripcion):"]
    for c in df.columns:
        lineas.append(f"- {c} ({df[c].dtype}): {descripcion_de(c)}")
    lineas.append("\nEstadisticas de columnas numericas:")
    lineas.append(df.describe().round(2).to_string())

    csv, n, truncado = _muestra_csv(df)
    if truncado:
        lineas.append(f"\nRegistros (muestra de las primeras {n} de {len(df)} filas, "
                      "en formato CSV):")
    else:
        lineas.append(f"\nRegistros completos ({n} filas, en formato CSV):")
    lineas.append(csv)
    return "\n".join(lineas), truncado


def _responder_con_ia(df: pd.DataFrame, pregunta: str) -> str:
    contexto, truncado = _contexto(df)
    nota = (" Si la pregunta es sobre un registro que no aparece en la muestra de "
            "filas proporcionada, indica que no esta en los datos disponibles."
            if truncado else "")
    prompt = (
        "Eres un asistente de analisis de datos. Responde de forma breve y precisa, "
        "en espaniol, usando UNICAMENTE la informacion del siguiente dataset, que "
        "incluye la descripcion de las columnas, estadisticas y los registros (filas) "
        "en formato CSV.\n\n"
        f"{contexto}\n\n"
        f"Pregunta del usuario: {pregunta}\n"
        "Si la pregunta pide un calculo, da el numero exacto." + nota
    )
    return preguntar_ia(prompt)


# --------------------------------------------------------------------------- #
def _normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def _buscar_columna(df: pd.DataFrame, texto: str):
    """Intenta detectar a que columna se refiere la pregunta."""
    t = _normalizar(texto)
    for col in df.columns:
        if _normalizar(col) in t or _normalizar(col).replace("_", " ") in t:
            return col
    return None


def _responder_local(df: pd.DataFrame, pregunta: str) -> str:
    """Motor de respuestas para preguntas frecuentes sin IA."""
    t = _normalizar(pregunta)

    if "cuantas columnas" in t or "numero de columnas" in t or "cantidad de columnas" in t:
        return f"El dataset tiene **{df.shape[1]} columnas**: {', '.join(df.columns)}."

    if ("cuantas filas" in t or "cuantos registros" in t or "numero de filas" in t
            or "cantidad de registros" in t):
        return f"El dataset tiene **{df.shape[0]} registros (filas)**."

    col = _buscar_columna(df, pregunta)

    if "media" in t or "promedio" in t:
        if col is not None and pd.api.types.is_numeric_dtype(df[col]):
            return f"La media del campo **{col}** es **{df[col].mean():.2f}**."
        return "Indica un campo numerico para calcular la media (ej. salario_usd)."

    if "mayor" in t or "maximo" in t or "max" in t:
        if col is not None and pd.api.types.is_numeric_dtype(df[col]):
            return f"El mayor valor del campo **{col}** es **{df[col].max()}**."
        if col is not None:
            return f"Valores del campo **{col}**: {', '.join(map(str, df[col].unique()[:15]))}."
        return "Indica un campo para conocer su valor maximo."

    if "menor" in t or "minimo" in t or "min" in t:
        if col is not None and pd.api.types.is_numeric_dtype(df[col]):
            return f"El menor valor del campo **{col}** es **{df[col].min()}**."
        return "Indica un campo numerico para conocer su valor minimo."

    if "frecuente" in t or "comun" in t or "moda" in t:
        if col is not None:
            moda = df[col].mode().iloc[0]
            return f"El valor mas frecuente del campo **{col}** es **{moda}**."
        return "Indica un campo para conocer su valor mas frecuente."

    if "suma" in t or "total" in t:
        if col is not None and pd.api.types.is_numeric_dtype(df[col]):
            return f"La suma del campo **{col}** es **{df[col].sum():.2f}**."

    if "mediana" in t:
        if col is not None and pd.api.types.is_numeric_dtype(df[col]):
            return f"La mediana del campo **{col}** es **{df[col].median():.2f}**."

    return (
        "No pude interpretar la pregunta con el motor interno. Prueba a reformularla "
        "(por ejemplo: '¿Cual es la media del campo salario_usd?') o configura una "
        "API key de IA en la barra lateral para respuestas mas flexibles."
    )
