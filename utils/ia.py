# -*- coding: utf-8 -*-
"""
Integracion con Gemini (Google) mediante la API REST.

Se usa la API REST con `requests` para evitar dependencias del SDK
deprecado `google.generativeai`. La clave se obtiene, en orden:
  1. st.secrets["GEMINI_API_KEY"]
  2. variable de entorno GEMINI_API_KEY
  3. lo que el usuario escriba en la barra lateral (session_state)

Los nombres de modelo de Gemini cambian con el tiempo (los 1.5 fueron
retirados en 2025). Por eso, en lugar de adivinar, se consulta a la API que
modelos admite la clave (ListModels) y se usa uno que soporte generateContent.
"""
import os
import requests
import streamlit as st

_BASE = "https://generativelanguage.googleapis.com/v1beta"
_URL_GENERAR = _BASE + "/models/{modelo}:generateContent"
_URL_LISTAR = _BASE + "/models"

# Lista de respaldo (modelos vigentes en 2026) por si ListModels falla
_MODELOS_RESPALDO = [
    "gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest",
    "gemini-2.5-flash-lite", "gemini-2.0-flash-001",
]


def obtener_api_key() -> str | None:
    """Recupera la API key de Gemini desde secrets, entorno o session_state."""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]
    return st.session_state.get("gemini_api_key") or None


def hay_api_key() -> bool:
    return bool(obtener_api_key())


@st.cache_data(show_spinner=False)
def _modelos_disponibles(api_key: str) -> list:
    """
    Consulta a la API que modelos soporta la clave para generateContent.
    Devuelve los nombres ordenados (se prefieren los 'flash', mas rapidos).
    Si la consulta falla, devuelve lista vacia (se usara el respaldo).
    """
    try:
        resp = requests.get(_URL_LISTAR, params={"key": api_key}, timeout=20)
        resp.raise_for_status()
    except Exception:
        return []

    modelos = []
    for m in resp.json().get("models", []):
        if "generateContent" in m.get("supportedGenerationMethods", []):
            modelos.append(m["name"].split("/")[-1])  # quitar prefijo 'models/'

    def prioridad(nombre: str) -> tuple:
        # Menor valor = mayor prioridad: flash > flash-lite > pro
        return (
            0 if "flash" in nombre else 1,
            0 if ("2.5" in nombre or "2.0" in nombre) else 1,
            1 if "pro" in nombre else 0,
            len(nombre),
        )

    modelos.sort(key=prioridad)
    return modelos


def preguntar_gemini(prompt: str, temperatura: float = 0.3) -> str:
    """
    Envia un prompt a Gemini y devuelve el texto de respuesta.
    Lanza RuntimeError con un mensaje claro si algo falla.
    """
    api_key = obtener_api_key()
    if not api_key:
        raise RuntimeError(
            "No hay una API key de Gemini configurada. Ingresala en la barra lateral."
        )

    # Modelos que admite la clave + respaldo (sin duplicados), probando los primeros
    disponibles = _modelos_disponibles(api_key)
    candidatos = disponibles + [m for m in _MODELOS_RESPALDO if m not in disponibles]
    candidatos = candidatos[:6]

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperatura},
    }
    ultimo_error = None
    for modelo in candidatos:
        try:
            resp = requests.post(
                _URL_GENERAR.format(modelo=modelo),
                params={"key": api_key},
                json=payload,
                timeout=30,
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            # 404 (modelo inexistente) / 400 (no soportado) -> probar el siguiente
            if resp.status_code in (400, 404):
                ultimo_error = f"Modelo {modelo}: {resp.status_code}."
                continue
            # 403 / 429 u otros: error de la clave o cuota, no seguir probando
            raise RuntimeError(f"Error {resp.status_code}: {resp.text[:200]}")
        except RuntimeError:
            raise
        except Exception as e:  # noqa: BLE001
            ultimo_error = str(e)

    disp = ", ".join(disponibles) if disponibles else "ninguno detectado"
    raise RuntimeError(
        (ultimo_error or "No se pudo contactar a Gemini.")
        + f" Modelos disponibles para tu clave: {disp}."
    )
