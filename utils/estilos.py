# -*- coding: utf-8 -*-
"""Estilos personalizados (CSS) inspirados en la plantilla DashboardKit.

Todo el aspecto visual se controla aqui con CSS inyectado: no se usan
librerias de componentes ni se modifica el tema nativo de Streamlit. La
funcionalidad de la app no cambia, solo su apariencia.

Uso: llamar a `aplicar_estilos()` una vez por render, desde `app.main()`.
"""
import streamlit as st

# Paleta y tokens extraidos de DashboardKit (SCSS settings):
#   primario #7267ef · fondo #f0f2f8 · sidebar #1c232f · tipografia Inter
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --ds-primary: #7267ef;
  --ds-primary-600: #5b50d6;
  --ds-primary-soft: rgba(114, 103, 239, 0.12);
  --ds-bg: #f0f2f8;
  --ds-sidebar: #1c232f;
  --ds-sidebar-brand: #161c25;
  --ds-sidebar-text: #eaedf3;
  --ds-sidebar-icon: #778290;
  --ds-card: #ffffff;
  --ds-heading: #1d2630;
  --ds-text: #3e4853;
  --ds-muted: #5b6b79;
  --ds-border: #e3e8ef;
  --ds-shadow: 0 2px 6px -1px rgba(0,0,0,0.10), 0 1px 3px rgba(0,0,0,0.05);
  --ds-radius: 10px;
  --ds-success: #17c666;
  --ds-danger: #ea4d4d;
  --ds-warning: #ffa21d;
  --ds-cyan: #3ec9d6;
}

/* ===================== Tipografia y fondo global ===================== */
html, body, .stApp, [data-testid="stAppViewContainer"] {
  font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
}
/* Preservar la fuente de iconos Material: evita que se vea el texto del
   ligature (p.ej. "keyboard_double_arrow_left", "expand_more") en vez del icono. */
[data-testid="stIconMaterial"],
span[class*="material-symbols"], span[class*="material-icons"],
.material-icons, .material-symbols-rounded, .material-symbols-outlined {
  font-family: 'Material Symbols Rounded', 'Material Symbols Outlined',
               'Material Icons' !important;
}
.stApp { background: var(--ds-bg); }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"] {
  padding-top: 2.4rem; padding-bottom: 3rem; max-width: 1400px;
}

h1, h2, h3, h4, h5 {
  color: var(--ds-heading) !important;
  font-weight: 600 !important; letter-spacing: -0.2px;
}
h1 { font-size: 1.85rem !important; }
h2 { font-size: 1.4rem !important; }
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li { color: var(--ds-text); }
a, a:visited { color: var(--ds-primary); text-decoration: none; }
a:hover { color: var(--ds-primary-600); }

/* ===================== Sidebar oscuro ===================== */
[data-testid="stSidebar"] {
  background: var(--ds-sidebar); border-right: none;
}
[data-testid="stSidebar"] * { color: var(--ds-sidebar-text); }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #ffffff !important; }

/* Forzar texto claro en enlaces del menu y captions (Streamlit los pinta
   oscuros con mayor especificidad que el selector global de arriba) */
[data-testid="stSidebarNav"] a span,
[data-testid="stSidebarNav"] a p,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] *,
[data-testid="stSidebar"] [data-testid="stExpander"] summary,
[data-testid="stSidebar"] [data-testid="stExpander"] summary * {
  color: var(--ds-sidebar-text) !important;
}

/* Marca superior */
[data-testid="stSidebar"] h2 { letter-spacing: 0.5px; }

/* Navegacion (st.navigation) */
[data-testid="stSidebarNav"] ul { padding: 0 8px; }
[data-testid="stSidebarNav"] a {
  border-radius: 8px; margin: 2px 0; padding: 8px 12px;
  transition: background 0.15s ease, color 0.15s ease;
}
[data-testid="stSidebarNav"] a:hover { background: rgba(255,255,255,0.06); }
[data-testid="stSidebarNav"] a[aria-current="page"] {
  background: var(--ds-primary);
}
[data-testid="stSidebarNav"] a[aria-current="page"] span,
[data-testid="stSidebarNav"] a[aria-current="page"] * { color: #ffffff !important; }
/* Titulos de grupo de la navegacion */
[data-testid="stSidebarNav"] [data-testid="stNavSectionHeader"] {
  color: var(--ds-sidebar-icon) !important;
  text-transform: uppercase; font-size: 0.72rem;
  letter-spacing: 0.6px; font-weight: 600;
}

/* Expander del sidebar (Configurar Gemini): que NO use el fondo claro del
   tema; transparente con borde sutil para integrarse en el sidebar oscuro. */
[data-testid="stSidebar"] [data-testid="stExpander"] {
  background: transparent !important;
  border: 1px solid #3a4452 !important; border-radius: 8px;
  box-shadow: none !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] details,
[data-testid="stSidebar"] [data-testid="stExpander"] summary,
[data-testid="stSidebar"] [data-testid="stExpanderDetails"] {
  background: transparent !important;
}

/* Inputs dentro del sidebar (p.ej. clave de Gemini): fondo oscuro legible.
   Se pinta el CONTENEDOR BaseWeb (no solo el <input>) para que el area del
   icono del ojo no quede en blanco. */
[data-testid="stSidebar"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-baseweb="base-input"],
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {
  background: #2a323f !important; color: #ffffff !important;
  border-color: #3a4452 !important;
}
/* Cursor (caret) y texto visibles: sobre el fondo oscuro el caret por defecto
   (oscuro) queda invisible al hacer click. Se fuerza el caret y el relleno de
   texto a blanco para que el cursor se vea al escribir la clave. */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {
  caret-color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
}
/* Boton de mostrar/ocultar clave (ojo): sin fondo blanco, icono claro */
[data-testid="stSidebar"] [data-baseweb="input"] button {
  background: transparent !important;
}
[data-testid="stSidebar"] [data-baseweb="input"] button:hover {
  background: rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] [data-baseweb="input"] svg {
  fill: #ced4dc !important; color: #ced4dc !important;
}
/* Ocultar el aviso "Press Enter to apply" dentro del sidebar */
[data-testid="stSidebar"] [data-testid="InputInstructions"] { display: none !important; }

/* Alertas dentro del sidebar (p.ej. "Clave guardada"): Streamlit usa fondos
   translucidos que sobre el sidebar oscuro quedan casi negros y ocultan el
   texto. Les damos fondo tintado opaco y texto claro para que contraste. */
[data-testid="stSidebar"] [data-testid="stAlert"] {
  background: rgba(23, 198, 102, 0.22) !important;
  border: 1px solid rgba(23, 198, 102, 0.55) !important;
}
[data-testid="stSidebar"] [data-testid="stAlert"] * { color: #eafff3 !important; }

/* Boton del popover "Acerca de esta app": transparente con texto claro, para
   no quedar texto claro sobre fondo claro en el sidebar oscuro. */
[data-testid="stSidebar"] [data-testid="stPopover"] button {
  background: transparent !important; border: 1px solid #3a4452 !important;
  color: var(--ds-sidebar-text) !important;
}
[data-testid="stSidebar"] [data-testid="stPopover"] button:hover {
  background: rgba(255,255,255,0.06) !important; color: #ffffff !important;
}
[data-testid="stSidebar"] [data-testid="stPopover"] button * {
  color: var(--ds-sidebar-text) !important;
}

/* ===================== Botones ===================== */
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
  background: var(--ds-primary); color: #ffffff; border: none;
  border-radius: 8px; padding: 0.5rem 1.1rem; font-weight: 500;
  box-shadow: 0 2px 6px rgba(114,103,239,0.30);
  transition: background 0.15s ease, transform 0.05s ease;
}
.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
  background: var(--ds-primary-600); color: #ffffff;
}
.stButton > button:active { transform: translateY(1px); }

/* El texto del boton va dentro de un stMarkdownContainer; su <p> lo pinta la
   regla global de parrafos (gris oscuro) y tapa el blanco del boton. Lo forzamos
   a blanco (con mayor especificidad) para que se lea en TODOS los botones del
   area principal, incluidos los 'secondary' como "Eliminar archivo". */
[data-testid="stMain"] .stButton > button p,
[data-testid="stMain"] .stButton > button span,
[data-testid="stMain"] .stDownloadButton > button p,
[data-testid="stMain"] .stDownloadButton > button span,
[data-testid="stMain"] .stFormSubmitButton > button p,
[data-testid="stMain"] .stFormSubmitButton > button span {
  color: #ffffff !important;
}

/* ===================== Metricas como tarjetas ===================== */
[data-testid="stMetric"] {
  background: var(--ds-card); border: 1px solid var(--ds-border);
  border-radius: var(--ds-radius); padding: 1rem 1.2rem;
  box-shadow: var(--ds-shadow);
}
[data-testid="stMetricLabel"] p { color: var(--ds-muted) !important; font-weight: 500; }
[data-testid="stMetricValue"] { color: var(--ds-heading); font-weight: 600; }
/* Tipografia uniforme en el valor de la metrica: misma fuente (Inter) y numeros
   normales (no tabulares), para que en valores como "$37K - $66K" los digitos no
   se vean con un estilo distinto al de las letras y simbolos. */
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
  font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif !important;
  font-variant-numeric: normal !important;
  font-feature-settings: normal !important;
}

/* ===================== Formularios como tarjeta ===================== */
[data-testid="stForm"] {
  background: var(--ds-card); border: 1px solid var(--ds-border);
  border-radius: var(--ds-radius); box-shadow: var(--ds-shadow);
  padding: 1.2rem 1.4rem;
}

/* ===================== Pestanas (tabs) ===================== */
[data-testid="stTabs"] [role="tablist"] {
  gap: 4px; border-bottom: 1px solid var(--ds-border);
}
[data-testid="stTabs"] button[role="tab"] {
  color: var(--ds-muted); font-weight: 500; padding: 0.4rem 0.9rem;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
  color: var(--ds-primary) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background: var(--ds-primary); }

/* ===================== Tablas / DataFrame ===================== */
[data-testid="stDataFrame"], [data-testid="stTable"] {
  border: 1px solid var(--ds-border); border-radius: var(--ds-radius);
  overflow: hidden; box-shadow: var(--ds-shadow); background: var(--ds-card);
}

/* ===================== Inputs ===================== */
[data-testid="stMain"] input,
[data-testid="stMain"] textarea,
[data-baseweb="select"] > div {
  border-radius: 8px !important; border-color: var(--ds-border) !important;
  background: var(--ds-card) !important;
}
[data-testid="stMain"] input:focus,
[data-testid="stMain"] textarea:focus {
  border-color: var(--ds-primary) !important;
  box-shadow: 0 0 0 3px var(--ds-primary-soft) !important;
}
/* El input INTERNO de los select / multiselect debe ser transparente: si toma
   el fondo blanco del input generico, aparece como una cajita que tapa los chips
   seleccionados cuando el control no tiene el foco. Aplica a TODOS los select. */
[data-baseweb="select"] input {
  background: transparent !important; box-shadow: none !important;
}

/* ===================== Expander / Popover ===================== */
[data-testid="stMain"] [data-testid="stExpander"] {
  border: 1px solid var(--ds-border); border-radius: var(--ds-radius);
  box-shadow: var(--ds-shadow); background: var(--ds-card); overflow: hidden;
}
[data-testid="stMain"] [data-testid="stExpander"] summary:hover { color: var(--ds-primary); }

/* ===================== Alertas (info/success/warning/error) ===================== */
[data-testid="stAlert"] { border-radius: var(--ds-radius); border: none; }

/* ===================== Multiselect (chips de seleccion) ===================== */
/* Por defecto Streamlit los pinta con su primario rojo; los pasamos al morado. */
[data-testid="stMain"] [data-baseweb="tag"] {
  background: var(--ds-primary) !important; border-radius: 6px !important;
}
[data-testid="stMain"] [data-baseweb="tag"] span,
[data-testid="stMain"] [data-baseweb="tag"] svg {
  color: #ffffff !important; fill: #ffffff !important;
}
[data-testid="stMain"] [data-baseweb="tag"] [role="button"]:hover {
  background: rgba(255,255,255,0.25) !important;
}

/* ===================== Entrada tipo chat (st.chat_input) ===================== */
/* El contenedor exterior es la UNICA superficie (tarjeta). */
[data-testid="stChatInput"] {
  border-radius: 14px !important; border: 1px solid var(--ds-border) !important;
  background: var(--ds-card) !important; box-shadow: var(--ds-shadow);
}
[data-testid="stChatInput"]:focus-within {
  border-color: var(--ds-primary) !important;
  box-shadow: 0 0 0 3px var(--ds-primary-soft) !important;
}
/* Interior (wrapper BaseWeb + textarea): transparente y sin borde para que no
   aparezca un segundo recuadro blanco con contorno gris dentro de la tarjeta. */
[data-testid="stChatInput"] [data-baseweb="textarea"],
[data-testid="stChatInput"] [data-baseweb="base-input"],
[data-testid="stChatInput"] textarea {
  background: transparent !important; border: none !important;
  box-shadow: none !important; color: var(--ds-heading) !important;
}
[data-testid="stChatInputSubmitButton"] { color: var(--ds-primary) !important; }
[data-testid="stChatInputSubmitButton"]:hover {
  color: var(--ds-primary-600) !important; background: var(--ds-primary-soft) !important;
}

/* ===================== Acentos en controles ===================== */
[data-baseweb="slider"] [role="slider"] { background: var(--ds-primary) !important; }
[data-baseweb="checkbox"] [data-checked="true"] { background: var(--ds-primary) !important; }

/* ===================== Contraste de textos secundarios ===================== */
/* Captions del area principal con gris legible (no el gris muy claro nativo) */
[data-testid="stMain"] [data-testid="stCaptionContainer"],
[data-testid="stMain"] [data-testid="stCaptionContainer"] * {
  color: var(--ds-muted) !important;
}
/* Texto de ayuda y placeholders con contraste suficiente */
[data-testid="stMain"] input::placeholder,
[data-testid="stMain"] textarea::placeholder { color: #97a3b0 !important; }

/* Divisores mas suaves */
hr, [data-testid="stDivider"] { border-color: var(--ds-border); }
</style>
"""


def aplicar_estilos() -> None:
    """Inyecta el CSS del tema DashboardKit. Idempotente por render."""
    st.markdown(_CSS, unsafe_allow_html=True)
