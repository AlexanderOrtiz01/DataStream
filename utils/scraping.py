# -*- coding: utf-8 -*-
"""
Lectura de opiniones desde la web (web scraping).

`scrape_url` descarga una pagina y extrae bloques de texto con aspecto de
opinion/comentario. Como las clases I-2026 pueden ejecutarse sin conexion
estable, se incluye un conjunto de opiniones de demostracion (resenas de
empleos en espaniol) para que el analisis siempre pueda mostrarse.
"""
import requests
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
}

# Opiniones de demostracion (resenas de estilo sobre empleos y empresas)
OPINIONES_DEMO = [
    "Excelente empresa para trabajar, el ambiente es genial y el salario muy competitivo.",
    "Pesimo lugar, sueldos bajos y los jefes no respetan los horarios. Una decepcion.",
    "Esta bien, el trabajo es estable pero las oportunidades de crecimiento son limitadas.",
    "Lo recomiendo muchisimo, gran cultura laboral y excelentes beneficios para el personal.",
    "Demasiada presion y horas extra sin pago, me arrepiento de haber aceptado el puesto.",
    "El equipo es maravilloso y el trabajo remoto me da una flexibilidad increible.",
    "Aburrido y repetitivo, las tareas son siempre lo mismo y no hay motivacion.",
    "Una empresa fantastica, capacitaciones constantes y un liderazgo que valora al empleado.",
    "Tiene algunos problemas de organizacion pero el sueldo y las prestaciones son solidos.",
    "Horrible gestion, mucha rotacion de personal y un clima laboral toxico.",
    "El trabajo me gusta bastante aunque la carga a veces es un poco frustrante.",
    "Excelente relacion entre esfuerzo y recompensa, contrato justo y buen ambiente.",
    "Salario insuficiente y cero reconocimiento, termine renunciando muy decepcionado.",
    "Buenas oficinas pero los procesos internos son lentos y burocraticos.",
    "Gran oportunidad de aprendizaje desde el primer dia, lo recomiendo totalmente.",
]


def scrape_url(url: str, max_items: int = 30) -> list:
    """
    Descarga la URL y extrae parrafos/comentarios con aspecto de opinion.
    Devuelve una lista de cadenas. Lanza excepcion si la descarga falla.
    """
    resp = requests.get(url, headers=_HEADERS, timeout=20)
    resp.raise_for_status()
    sopa = BeautifulSoup(resp.text, "lxml")

    # Se eliminan elementos no informativos
    for etiqueta in sopa(["script", "style", "nav", "header", "footer", "noscript"]):
        etiqueta.decompose()

    candidatos = []
    # Selectores frecuentes para comentarios/resenas + parrafos genericos
    for sel in ["[class*=comment]", "[class*=review]", "[class*=opinion]",
                "[class*=coment]", "blockquote", "p", "li"]:
        for nodo in sopa.select(sel):
            texto = " ".join(nodo.get_text(" ", strip=True).split())
            # Se filtran textos demasiado cortos o demasiado largos
            if 25 <= len(texto) <= 400:
                candidatos.append(texto)

    # Quitar duplicados conservando el orden
    vistos = set()
    opiniones = []
    for t in candidatos:
        if t not in vistos:
            vistos.add(t)
            opiniones.append(t)
        if len(opiniones) >= max_items:
            break
    return opiniones
