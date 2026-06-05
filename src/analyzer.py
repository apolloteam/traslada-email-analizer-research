"""
analyzer.py — Analiza correos con Claude y decide qué acción tomar.
"""

import os
import anthropic
from dotenv import load_dotenv
load_dotenv()

from models.email_decision import EmailDecision
from utils.email_parser import extraer_texto_body

MODELO = "claude-sonnet-4-6"
_DEFAULT_RULES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "general_rules.md")


class AnalizadorClaude:
    def __init__(self, rules_path: str = _DEFAULT_RULES):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )

        self.rules_path = rules_path

    def _cargar_reglas(self) -> str:
        with open(self.rules_path, encoding="utf-8") as f:
            contenido = f.read()
        return contenido

    def analizar(self, correo: dict) -> dict:
        """
        Le pasa el correo y las reglas a Claude.
        Devuelve un dict con: accion, razon, datos_extra
        """

        remitente = correo["from"]["emailAddress"]["address"]
        asunto    = correo.get("subject", "(sin asunto)")
        cuerpo    = extraer_texto_body(correo)
        fecha     = correo.get("receivedDateTime", "")
        reglas_generales    = self._cargar_reglas()

        SYSTEM_PROMPT = f"""
Sos un agente de correo empresarial. Analizá el correo recibido y decidí qué acción tomar según las reglas de la empresa.

# Reglas de la empresa
{reglas_generales}

# Campos de la respuesta
- accion: "responder" | "reenviar" | "responder_y_reenviar" | "ignorar"
- razon: explicación breve de la decisión
- respuesta_html: cuerpo HTML de la respuesta (solo si accion incluye responder, sino null)
- reenviar_a: lista de emails destino (solo si accion incluye reenviar, sino [])
- comentario_reenvio: texto opcional que acompaña el reenvío
- prioridad: "alta" | "media" | "baja"

Si ninguna regla aplica, usá "ignorar". La respuesta_html debe ser profesional y en el mismo idioma que el correo recibido.
""".strip()

        prompt = f"""
# Correo recibido
- **Remitente:** {remitente}
- **Fecha:** {fecha}
- **Asunto:** {asunto}
- **Cuerpo:**
{cuerpo}
"""
        response = self.client.messages.parse(
            model=MODELO,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            output_format=EmailDecision,
        )

        decision = response.parsed_output.model_dump()
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
