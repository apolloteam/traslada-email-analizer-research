"""
email_parser.py — Extrae y normaliza el texto plano del cuerpo de un correo electrónico.
"""

import re
import unicodedata
from bs4 import BeautifulSoup


# Caracteres Unicode invisibles usados por plataformas de email marketing para
# evadir filtros de spam. Se normalizan antes de enviar el texto al LLM.
_CHARS_A_ESPACIO = frozenset([
    "\xa0",    # NO-BREAK SPACE
    " ",  # FIGURE SPACE
])
_CHARS_ELIMINAR = frozenset([
    "͏",  # COMBINING GRAPHEME JOINER
    "­",  # SOFT HYPHEN
    "​",  # ZERO WIDTH SPACE
    "‌",  # ZERO WIDTH NON-JOINER
    "‍",  # ZERO WIDTH JOINER
    "‎",  # LEFT-TO-RIGHT MARK
    "‏",  # RIGHT-TO-LEFT MARK
    "⁠",  # WORD JOINER
])


def extraer_texto_body(correo: dict) -> str:
    """Extrae texto plano del body HTML de un correo, normalizando caracteres invisibles."""
    html = correo.get("body", {}).get("content", "")
    if not html:
        return correo.get("bodyPreview", "")

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["style", "script", "head", "meta", "link"]):
        tag.decompose()

    texto = soup.get_text(separator=" ")
    texto = "".join(
        " " if c in _CHARS_A_ESPACIO else
        "" if unicodedata.category(c) == "Cf" or c in _CHARS_ELIMINAR else
        c
        for c in texto
    )
    # Limpia whitespace preservando saltos de línea para que el LLM entienda la estructura.
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    resultado = texto.strip()[:4000]
    return resultado
