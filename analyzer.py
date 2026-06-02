"""
analyzer.py — Analiza correos con Claude y decide qué acción tomar.
"""

import os
import re
import json
import unicodedata
import anthropic
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

MODELO = "claude-sonnet-4-6" #"claude-sonnet-4-20250514"

# Caracteres Unicode invisibles usados por plataformas de email marketing para
# evadir filtros de spam. Se normalizan antes de enviar el texto al LLM.
_CHARS_A_ESPACIO = frozenset([
    "\xa0",    # NO-BREAK SPACE
    " ",  # FIGURE SPACE
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


class AnalizadorClaude:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def _extraer_texto_body(self, correo: dict) -> str:
        """Extrae texto plano del body HTML del correo."""
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
        texto = texto.strip()[:4000]
        return texto

    def analizar(self, correo: dict, reglas: list[dict]) -> dict:
        """
        Le pasa el correo y las reglas a Claude.
        Devuelve un dict con: accion, razon, datos_extra
        """

        remitente = correo["from"]["emailAddress"]["address"]
        asunto    = correo.get("subject", "(sin asunto)")
        cuerpo    = self._extraer_texto_body(correo)
        fecha     = correo.get("receivedDateTime", "")

        reglas_texto = json.dumps(reglas, ensure_ascii=False, indent=2)

        prompt = f"""Sos un agente de correo empresarial. Analizá el siguiente correo y decidí qué acción tomar según las reglas de la empresa.

## Correo recibido
- **Remitente:** {remitente}
- **Fecha:** {fecha}
- **Asunto:** {asunto}
- **Cuerpo:**
{cuerpo}

## Reglas de la empresa
{reglas_texto}

## Tu tarea
Analizá el correo y devolvé ÚNICAMENTE un objeto JSON válido con esta estructura exacta:

{{
  "accion": "responder" | "reenviar" | "responder_y_reenviar" | "ignorar",
  "razon": "explicación breve de por qué tomás esta decisión",
  "respuesta_html": "cuerpo HTML de la respuesta (solo si accion es responder o responder_y_reenviar, sino null)",
  "reenviar_a": ["email1@empresa.com"] (solo si accion es reenviar o responder_y_reenviar, sino []),
  "comentario_reenvio": "texto opcional que acompaña el reenvío",
  "prioridad": "alta" | "media" | "baja"
}}

Importante:
- Si ninguna regla aplica, usá "ignorar".
- La respuesta_html debe ser profesional y en el mismo idioma que el correo recibido.
- No incluyas nada fuera del JSON.
"""

        message = self.client.messages.create(
            model=MODELO,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        texto = message.content[0].text.strip()

        # Limpiar posibles backticks si Claude los agrega
        if texto.startswith("```"):
            texto = texto.split("```")[1]
            if texto.startswith("json"):
                texto = texto[4:]
        texto = texto.strip()

        decision = json.loads(texto)
        return decision

    def generar_respuesta_personalizada(self, correo: dict, instruccion: str) -> str:
        """
        Genera una respuesta HTML personalizada con una instrucción específica.
        Útil para reglas que necesitan respuestas más elaboradas.
        """
        asunto = correo.get("subject", "")
        cuerpo = correo.get("bodyPreview", "")
        remitente = correo["from"]["emailAddress"]["address"]

        prompt = f"""Generá una respuesta profesional en HTML para este correo.

Instrucción: {instruccion}

Correo original:
- De: {remitente}
- Asunto: {asunto}
- Cuerpo: {cuerpo}

Devolvé solo el HTML del cuerpo del email, sin <html> ni <body>. Usá el mismo idioma que el correo original."""

        message = self.client.messages.create(
            model=MODELO,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
