# -*- coding: utf-8 -*-
"""
Deteccion de comentarios/opiniones reales.

Filtra fragmentos de texto (pegados a mano o extraidos de la web) para quedarse
solo con los que parecen un comentario u opinion de lenguaje natural, descartando
ruido tipico de las paginas web: menus de navegacion, fechas, URLs, avisos de
cookies/login, titulares sueltos, codigos o numeros, etc.

Funcion principal:
    filtrar_opiniones(lista) -> {"opiniones": [...], "descartadas": [(texto, motivo), ...]}
"""
import re
import unicodedata

from utils.sentimiento import _POSITIVAS, _NEGATIVAS

# Limites de longitud razonables para un comentario
_MIN_CARACTERES = 20
_MAX_CARACTERES = 700
_MIN_PALABRAS = 4
# Proporcion minima de letras (descarta fechas, codigos, precios, simbolos)
_MIN_RATIO_LETRAS = 0.55

# Palabras funcionales comunes (ES + EN): casi todo texto en lenguaje natural
# contiene alguna; los menus y codigos normalmente no.
_FUNCIONALES = {
    # espaniol
    "de", "la", "que", "el", "en", "y", "a", "los", "un", "por", "con", "no",
    "una", "su", "para", "es", "al", "lo", "como", "mas", "pero", "sus", "le",
    "ya", "o", "este", "si", "porque", "esta", "entre", "cuando", "muy", "sin",
    "sobre", "tambien", "me", "hasta", "hay", "donde", "han", "quien", "estan",
    "estado", "desde", "todo", "nos", "durante", "todos", "uno", "les", "ni",
    "yo", "mi", "te", "tu", "del", "se", "son", "fue", "ha", "era",
    # ingles
    "the", "and", "to", "of", "in", "is", "it", "you", "that", "was", "for",
    "on", "are", "with", "as", "they", "this", "have", "be", "at", "but", "not",
    "your", "from", "or", "had", "by", "we", "my", "me", "so", "i",
}

# Frases/patrones tipicos de relleno web (se comparan normalizados, sin tildes)
_BLOQUEADAS = [
    "cookie", "politica de privacidad", "terminos y condiciones", "terminos de uso",
    "todos los derechos", "derechos reservados", "iniciar sesion", "inicia sesion",
    "registrate", "registrese", "suscribete", "suscripcion", "by continuing",
    "user agreement", "privacy policy", "sign in", "log in", "create account",
    "lee tambien", "leer mas", "ver mas", "compartir en", "comparte este",
    "publicidad", "newsletter", "boletin", "copyright", "siguenos", "menu principal",
    "advertisement", "subscribe", "follow us", "share this", "read more",
    "accept all", "aceptar todas", "configurar cookies", "cargando", "javascript",
    "habilita", "navegador", "continuar leyendo", "deja tu comentario",
    "agree to", "privacy", "all rights reserved",
    # Interfaz de redes sociales (LinkedIn, Facebook, etc.). Solo frases largas y
    # distintivas: los botones cortos ("Me gusta", "Responder") ya los descarta la
    # regla de "muy pocas palabras", y como subcadenas darian falsos negativos.
    "ver enlace grafico", "abrir el teclado", "teclado de emoji",
    "orden actual seleccionado", "comentario del comentario",
    "ver mas comentarios", "cargar mas comentarios", "ver traduccion",
    "mostrar traduccion", "anadir a tu red", "mostrar mas respuestas",
]


def _normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def clasificar_texto(texto: str):
    """Decide si un fragmento parece un comentario/opinion real.

    Devuelve (es_opinion: bool, motivo: str). 'motivo' explica por que se acepto
    o por que se descarto (util para mostrarlo en la interfaz).
    """
    t = " ".join(str(texto).split())  # colapsa espacios y saltos de linea
    if not t:
        return False, "vacio"

    norm = _normalizar(t)

    # 1) Longitud
    if len(t) < _MIN_CARACTERES:
        return False, "demasiado corto"
    if len(t) > _MAX_CARACTERES:
        return False, "demasiado largo (probable bloque de texto, no un comentario)"

    # 2) URL o correo suelto
    if re.match(r"^\s*(https?://|www\.)\S+\s*$", t) or re.match(r"^\S+@\S+\.\S+$", t):
        return False, "es un enlace o correo"

    # 2b) Fecha o metadato de publicacion ("Publicado el ...", "Actualizado ...")
    if re.match(r"^(publicad|actualizad|published|updated|hace\s+\d)", norm):
        return False, "metadato de fecha/publicacion"
    _meses = (r"enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|"
              r"octubre|noviembre|diciembre|january|february|march|april|may|june|"
              r"july|august|september|october|november|december")
    if (re.search(r"\b(" + _meses + r")\b", norm)
            and re.search(r"\b\d{4}\b", norm)
            and len(t.split()) < 8):
        return False, "linea de fecha"

    # 2c) Contador de interfaz ("1 comentario...", "3 respuestas", "5 reactions")
    if re.match(r"^\d+\s+(comentario|coment|comment|respuesta|reply|"
                r"reaccion|reaction|me gusta|like)", norm):
        return False, "contador de interfaz (comentarios/respuestas)"

    # 2d) Cabecera o cargo con separadores (tipico de perfiles de LinkedIn:
    # "Socio Fundador | Pentest | Forense" o "CEO · Co-founder · Nearshore").
    if t.count("|") >= 1 or t.count("·") >= 2 or t.count("•") >= 1:
        return False, "cabecera/cargo con separadores (no es un comentario)"

    # 3) Numero de palabras
    palabras = re.findall(r"[a-zñáéíóúü]+", t.lower())
    if len(palabras) < _MIN_PALABRAS:
        return False, "muy pocas palabras"

    # 4) Proporcion de letras (descarta fechas, precios, codigos, tablas)
    letras = sum(c.isalpha() for c in t)
    if letras / len(t) < _MIN_RATIO_LETRAS:
        return False, "demasiados numeros o simbolos (no parece texto)"

    # 5) Sin minusculas -> titular/menu en mayusculas
    if not any(c.islower() for c in t):
        return False, "todo en mayusculas (parece un titulo o menu)"

    # 6) Relleno web conocido (cookies, login, suscripciones, etc.)
    for frase in _BLOQUEADAS:
        if frase in norm:
            return False, f"texto de relleno web ('{frase}')"

    tiene_puntuacion = bool(re.search(r"[,.;:!?]", t))

    # 7) Lenguaje natural: una frase real suele traer conectores comunes
    # (de, la, the, and...) o puntuacion de oracion. Si no tiene ninguno de los
    # dos, parece un menu o lista de etiquetas (ej. "Inicio Noticias Deportes").
    tiene_conector = any(p in _FUNCIONALES for p in palabras)
    if not tiene_conector and not tiene_puntuacion:
        return False, "no parece una frase (sin conectores ni puntuacion)"

    # 8) Nombre propio o titulo: sin puntuacion de oracion y con casi todas las
    # palabras de contenido en mayuscula inicial (ej. "Miguel Angel Romero de
    # los Llanos"). Los comentarios reales mezclan palabras en minuscula.
    if not tiene_puntuacion:
        contenido = [w for w in t.split()
                     if w.lower() not in _FUNCIONALES and len(w) > 1 and w[0].isalpha()]
        if len(contenido) >= 2:
            capitalizadas = sum(1 for w in contenido if w[0].isupper())
            if capitalizadas / len(contenido) >= 0.8:
                return False, "parece un nombre propio o titulo, no un comentario"

    # Senal positiva: si ademas trae palabras de opinion, lo indicamos
    tiene_sentimiento = any(p in _POSITIVAS or p in _NEGATIVAS for p in palabras)
    motivo = "comentario con carga de opinion" if tiene_sentimiento else "frase de lenguaje natural"
    return True, motivo


def filtrar_opiniones(lista) -> dict:
    """Separa una lista de fragmentos en opiniones validas y descartadas (heuristica).

    Devuelve {"opiniones": [str, ...], "descartadas": [(texto, motivo), ...]}.
    """
    opiniones, descartadas = [], []
    for texto in lista:
        ok, motivo = clasificar_texto(texto)
        if ok:
            opiniones.append(" ".join(str(texto).split()))
        else:
            descartadas.append((str(texto).strip(), motivo))
    return {"opiniones": opiniones, "descartadas": descartadas}


_MOTIVO_DESCARTE = "no parece un comentario u opinion"


def _filtrar_opiniones_ia(lista) -> dict:
    """Separa comentarios reales del resto pidiendoselo al modelo de lenguaje.

    Devuelve el mismo formato que `filtrar_opiniones`. Lanza excepcion si la
    respuesta del modelo no se puede interpretar (para poder caer a la heuristica).
    """
    from utils.ia import preguntar_ia

    textos = [" ".join(str(t).split()) for t in lista]
    enumeradas = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(textos))
    prompt = (
        "A continuacion hay una lista numerada de fragmentos de texto extraidos de "
        "una pagina web o red social. Identifica cuales son COMENTARIOS u OPINIONES "
        "reales escritos por personas (resenas, valoraciones, comentarios con una "
        "idea u opinion).\n"
        "DESCARTA todo lo demas: titulos de puesto o cargo profesional, nombres de "
        "personas sueltos, elementos de interfaz (botones, 'Ver mas', 'Me gusta', "
        "'Responder', contadores de comentarios), fechas, anuncios, menus de "
        "navegacion, avisos de cookies o de inicio de sesion, y enlaces.\n"
        "Responde UNICAMENTE con los numeros de los fragmentos que SI son comentarios "
        "u opiniones, separados por comas (ejemplo: 2, 5, 6). Si ninguno lo es, "
        "responde exactamente 'ninguno'. No agregues explicaciones.\n\n"
        + enumeradas
    )
    respuesta = preguntar_ia(prompt, temperatura=0.0)

    numeros = {int(n) for n in re.findall(r"\d+", respuesta)}
    validos = {n for n in numeros if 1 <= n <= len(textos)}
    if not validos and "ninguno" not in respuesta.lower():
        raise RuntimeError("Respuesta del modelo no interpretable")

    opiniones, descartadas = [], []
    for i, t in enumerate(textos):
        if (i + 1) in validos:
            opiniones.append(t)
        else:
            descartadas.append((t, _MOTIVO_DESCARTE))
    return {"opiniones": opiniones, "descartadas": descartadas}


def filtrar_comentarios(lista) -> dict:
    """Filtra comentarios reales del resto del texto.

    Usa el modelo de lenguaje si hay una clave configurada (mas preciso); si no
    esta disponible o falla, recurre a la heuristica local. Es transparente para
    quien lo llama: siempre devuelve {"opiniones": [...], "descartadas": [...]}.
    """
    try:
        from utils.ia import hay_api_key
    except Exception:
        hay_api_key = lambda: False  # noqa: E731

    if hay_api_key():
        try:
            return _filtrar_opiniones_ia(lista)
        except Exception:
            pass  # silencioso: si la IA falla, se usa la heuristica
    return filtrar_opiniones(lista)
