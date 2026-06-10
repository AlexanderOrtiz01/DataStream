# -*- coding: utf-8 -*-
"""Almacen en memoria de sesion para el archivo que carga el usuario.

Permite que un archivo subido en la seccion de Carga de Archivos quede
disponible en otras secciones (por ejemplo, la Interfaz IA) y persista mientras
dure la sesion, hasta que el usuario decida eliminarlo.
"""
import pandas as pd
import streamlit as st

_KEY_DF = "archivo_usuario_df"
_KEY_NOMBRE = "archivo_usuario_nombre"


def guardar_archivo(nombre: str, df: pd.DataFrame) -> None:
    """Guarda (o reemplaza) el archivo del usuario en la sesion."""
    st.session_state[_KEY_DF] = df
    st.session_state[_KEY_NOMBRE] = nombre


def hay_archivo() -> bool:
    """True si hay un archivo del usuario guardado en la sesion."""
    return st.session_state.get(_KEY_DF) is not None


def obtener_df():
    """DataFrame del archivo guardado (o None)."""
    return st.session_state.get(_KEY_DF)


def obtener_nombre():
    """Nombre del archivo guardado (o None)."""
    return st.session_state.get(_KEY_NOMBRE)


def eliminar_archivo() -> None:
    """Elimina el archivo guardado de la sesion."""
    st.session_state.pop(_KEY_DF, None)
    st.session_state.pop(_KEY_NOMBRE, None)
