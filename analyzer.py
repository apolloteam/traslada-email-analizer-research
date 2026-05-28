"""
analyzer.py — Analiza correos con Claude y decide qué acción tomar.
"""

import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

MODELO = "claude-sonnet-4-6" #"claude-sonnet-4-20250514"


class AnalizadorClaude:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def analizar(self, correo: dict, reglas: list[dict]) -> dict:
        """
        Le pasa el correo y las reglas a Claude.
        Devuelve un dict con: accion, razon, datos_extra
        """

        # Extraer texto limpio del correo
        remitente   = correo["from"]["emailAddress"]["address"]
        asunto      = correo.get("subject", "(sin asunto)")
        cuerpo      = correo.get("bodyPreview", "")  # primeros 255 chars
        fecha       = correo.get("receivedDateTime", "")

        # Si el bodyPreview es muy corto, usamos el body completo (HTML → texto)
        if len(cuerpo) < 100 and correo.get("body"):
            cuerpo = correo["body"].get("content", cuerpo)
            # Quitar tags HTML básicos
            import re
            cuerpo = re.sub(r"<[^>]+>", " ", cuerpo)
            cuerpo = re.sub(r"\s+", " ", cuerpo).strip()[:2000]

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
