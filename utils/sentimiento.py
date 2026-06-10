# -*- coding: utf-8 -*-
"""
Analisis de sentimientos.

Dos motores:
  - 'lexico': analizador propio basado en un diccionario de palabras en
    espaniol (funciona siempre, sin internet ni API).
  - 'gemini': clasificacion mediante el modelo de IA (mas preciso).
"""
import re
import unicodedata

# Lexicos en espaniol (palabras base, sin tildes para comparar normalizado)
_POSITIVAS = {
    "bueno", "buena", "excelente", "genial", "increible", "maravilloso",
    "fantastico", "encanta", "encanto", "encantar", "perfecto", "perfecta",
    "recomiendo", "recomendado", "divertido", "divertida", "adictivo",
    "espectacular", "impresionante", "mejor", "favorito", "obra", "maestra",
    "disfrute", "disfruto", "satisfecho", "feliz", "contento", "calidad",
    "amo", "amor", "agil", "fluido", "hermoso", "bonito", "solido", "epico",
    "facil", "rapido", "barato", "vale", "pena", "gusta", "gusto", "brillante",
}
_NEGATIVAS = {
    "malo", "mala", "horrible", "terrible", "pesimo", "pesima", "aburrido",
    "aburrida", "decepcion", "decepcionante", "odio", "odia", "lento",
    "lenta", "caro", "cara", "bug", "bugs", "error", "errores", "fallo",
    "fallos", "problema", "problemas", "basura", "estafa", "horrendo",
    "frustrante", "injugable", "roto", "rota", "peor", "fatal", "deficiente",
    "insufrible", "tedioso", "repetitivo", "vacio", "vacia", "decepciono",
    "arrepiento", "molesto", "feo", "fea", "incompleto", "abandonado",
}
_NEGADORES = {"no", "nunca", "jamas", "tampoco", "sin", "ni"}


def _normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto


def analizar_lexico(texto: str) -> dict:
    """
    Devuelve {'sentimiento': 'Positivo'|'Negativo'|'Neutral',
              'puntaje': float, 'positivas': int, 'negativas': int}.
    Se contemplan negadores simples (ej. 'no me gusta' invierte el signo).
    """
    palabras = re.findall(r"[a-z]+", _normalizar(texto))
    pos = neg = 0
    for i, p in enumerate(palabras):
        negado = i > 0 and palabras[i - 1] in _NEGADORES
        if p in _POSITIVAS:
            if negado:
                neg += 1
            else:
                pos += 1
        elif p in _NEGATIVAS:
            if negado:
                pos += 1
            else:
                neg += 1
    total = pos + neg
    puntaje = 0.0 if total == 0 else (pos - neg) / total
    if puntaje > 0.1:
        etiqueta = "Positivo"
    elif puntaje < -0.1:
        etiqueta = "Negativo"
    else:
        etiqueta = "Neutral"
    return {"sentimiento": etiqueta, "puntaje": round(puntaje, 3),
            "positivas": pos, "negativas": neg}


def analizar_gemini(textos: list) -> list:
    """
    Clasifica una lista de opiniones con Gemini en un solo prompt.
    Devuelve una lista de etiquetas ('Positivo'/'Negativo'/'Neutral').
    Si algo falla, lanza la excepcion para que el llamador haga fallback.
    """
    from utils.ia import preguntar_gemini
    enumeradas = "\n".join(f"{i+1}. {t}" for i, t in enumerate(textos))
    prompt = (
        "Clasifica el sentimiento de cada una de las siguientes opiniones sobre "
        "empleos y empresas en EXACTAMENTE una palabra: Positivo, Negativo o Neutral.\n"
        "Responde solo con el numero y la etiqueta, un resultado por linea, "
        "sin explicaciones.\n\n" + enumeradas
    )
    respuesta = preguntar_gemini(prompt, temperatura=0.0)
    etiquetas = []
    for linea in respuesta.splitlines():
        l = linea.lower()
        if "positiv" in l:
            etiquetas.append("Positivo")
        elif "negativ" in l:
            etiquetas.append("Negativo")
        elif "neutral" in l or "neutro" in l:
            etiquetas.append("Neutral")
    # Si el modelo no devolvio una etiqueta por opinion, se completa neutral
    while len(etiquetas) < len(textos):
        etiquetas.append("Neutral")
    return etiquetas[: len(textos)]
