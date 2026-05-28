"""
mail_client.py — Interacción con Outlook 365 via Microsoft Graph API
"""

import os
import requests
import msal # Microsoft Authentication Library para obtener tokens OAuth2.
from dotenv import load_dotenv

load_dotenv()

GRAPH = "https://graph.microsoft.com/v1.0"
CATEGORIA_PROCESADO = "AgenteProcesado"   # categoría que se crea en Outlook


class MailClient:
    def __init__(self):
        self.client_id     = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.tenant_id     = os.getenv("TENANT_ID")
        self.user_email    = os.getenv("USER_EMAIL")
        self._token        = None

    # ── Auth ──────────────────────────────────────────────────────

    def _get_token(self) -> str:
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            client_credential=self.client_secret,
        )
        result = app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )
        if "access_token" not in result:
            raise Exception(f"Auth fallida: {result.get('error_description')}")
        return result["access_token"]

    def _headers(self) -> dict:
        # Renueva el token en cada llamada (MSAL cachea internamente)
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }

    # ── Leer ──────────────────────────────────────────────────────

    def leer_no_procesados(self, cantidad: int = 20) -> list[dict]:
        """
        Lee correos que NO tienen la categoría 'AgenteProcesado'.
        Así el agente nunca reprocesa el mismo mail.
        """
        params = {
            "$top": cantidad,
            "$select": "id,subject,from,toRecipients,body,bodyPreview,receivedDateTime,isRead",
            "$orderby": "receivedDateTime asc",
            # Excluye los ya procesados por el agente
            "$filter": f"NOT categories/any(c:c eq '{CATEGORIA_PROCESADO}')",
        }
        url = f"{GRAPH}/users/{self.user_email}/messages"
        r = requests.get(url, headers=self._headers(), params=params)
        r.raise_for_status()
        return r.json().get("value", [])

    def leer_completo(self, message_id: str) -> dict:
        """Obtiene el cuerpo completo de un correo."""
        url = f"{GRAPH}/users/{self.user_email}/messages/{message_id}"
        r = requests.get(url, headers=self._headers())
        r.raise_for_status()
        return r.json()

    # ── Acciones ──────────────────────────────────────────────────

    def responder(self, message_id: str, cuerpo_html: str) -> None:
        """Responde al correo original."""
        url = f"{GRAPH}/users/{self.user_email}/messages/{message_id}/reply"
        payload = {
            "message": {
                "body": {"contentType": "HTML", "content": cuerpo_html}
            },
            "comment": ""
        }
        r = requests.post(url, headers=self._headers(), json=payload)
        r.raise_for_status()

    def reenviar(self, message_id: str, destinatarios: list[str], comentario: str = "") -> None:
        """Reenvía el correo a una lista de destinatarios."""
        to_list = [{"emailAddress": {"address": e}} for e in destinatarios]
        url = f"{GRAPH}/users/{self.user_email}/messages/{message_id}/forward"
        payload = {
            "comment": comentario,
            "toRecipients": to_list,
        }
        r = requests.post(url, headers=self._headers(), json=payload)
        r.raise_for_status()

    def enviar_nuevo(self, destinatario: str, asunto: str, cuerpo_html: str) -> None:
        """Envía un correo nuevo (no como respuesta)."""
        url = f"{GRAPH}/users/{self.user_email}/sendMail"
        payload = {
            "message": {
                "subject": asunto,
                "body": {"contentType": "HTML", "content": cuerpo_html},
                "toRecipients": [{"emailAddress": {"address": destinatario}}],
            },
            "saveToSentItems": True,
        }
        r = requests.post(url, headers=self._headers(), json=payload)
        r.raise_for_status()

    def marcar_procesado(self, message_id: str) -> None:
        """
        Agrega la categoría 'AgenteProcesado' al correo.
        Así el agente no lo vuelve a procesar en el próximo ciclo.
        """
        url = f"{GRAPH}/users/{self.user_email}/messages/{message_id}"
        payload = {"categories": [CATEGORIA_PROCESADO]}
        r = requests.patch(url, headers=self._headers(), json=payload)
        r.raise_for_status()

    def marcar_leido(self, message_id: str) -> None:
        url = f"{GRAPH}/users/{self.user_email}/messages/{message_id}"
        r = requests.patch(url, headers=self._headers(), json={"isRead": True})
        r.raise_for_status()
