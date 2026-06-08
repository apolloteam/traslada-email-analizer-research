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
    def __init__(self, buzon: str):
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.tenant_id = os.getenv("TENANT_ID")
        self.buzon = buzon
        self._token = None
        self._folder_cache: dict[str, str] = {}  # nombre → folder_id

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
            raise Exception(f"Auth office 365 fallida: {result.get('error_description')}")
        return result["access_token"]

    def refresh_token(self) -> None:
        """Obtiene un token fresco y lo cachea para todo el ciclo."""
        self._token = self._get_token()

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    # ── Leer ──────────────────────────────────────────────────────

    def leer_no_procesados(self, cantidad: int = 20) -> list[dict]:
        """
        Lee correos que NO tienen la categoría 'AgenteProcesado'.
        Así el agente nunca reprocesa el mismo mail.
        """

        # NOTA: El paréntesis en $select es solo para concatenar el string sin 
        # que se rompa la línea (lo une en tiempo de compilación, no tiene costo). 
        # No es parte de la sintaxis de Microsoft Graph.
        params = {
            "$top": cantidad,
            "$select": (
                "id,"
                "internetMessageId,"
                "conversationId,"
                "subject,"
                "from,"
                "toRecipients,"
                "ccRecipients,"
                "replyTo,"
                "bodyPreview,"
                "body,"
                "receivedDateTime,"
                "isRead,"
                "sentDateTime,"
                "hasAttachments,"
                "importance,"
                "parentFolderId"
            ),
            "$orderby": "receivedDateTime asc",
            # Excluye los ya procesados por el agente
            "$filter": f"NOT categories/any(c:c eq '{CATEGORIA_PROCESADO}')",
        }
        url = f"{GRAPH}/users/{self.buzon}/messages"
        r = requests.get(url, headers=self._headers(), params=params)
        r.raise_for_status()
        resp = r.json().get("value", [])
        
        return resp

    def leer_completo(self, message_id: str) -> dict:
        """Obtiene el cuerpo completo de un correo."""
        url = f"{GRAPH}/users/{self.buzon}/messages/{message_id}"
        r = requests.get(url, headers=self._headers())
        r.raise_for_status()
        return r.json()

    # ── Acciones ──────────────────────────────────────────────────

    def responder(self, message_id: str, cuerpo_html: str) -> None:
        """Responde al correo original."""
        url = f"{GRAPH}/users/{self.buzon}/messages/{message_id}/reply"
        payload = {
            "message": {
                "body": {"contentType": "HTML", "content": cuerpo_html}
            },
            "comment": ""
        }
        r = requests.post(url, headers=self._headers(), json=payload)
        r.raise_for_status()

    def crear_draft_respuesta(self, message_id: str, cuerpo_html: str) -> None:
        """Crea un borrador de respuesta en la carpeta Drafts sin enviarlo."""
        url = f"{GRAPH}/users/{self.buzon}/messages/{message_id}/createReply"
        payload = {
            "message": {
                "body": {"contentType": "HTML", "content": cuerpo_html}
            }
        }
        r = requests.post(url, headers=self._headers(), json=payload)
        r.raise_for_status()

    def reenviar(self, message_id: str, destinatarios: list[str], comentario: str = "") -> None:
        """Reenvía el correo a una lista de destinatarios."""
        to_list = [{"emailAddress": {"address": e}} for e in destinatarios]
        url = f"{GRAPH}/users/{self.buzon}/messages/{message_id}/forward"
        payload = {
            "comment": comentario,
            "toRecipients": to_list,
        }
        r = requests.post(url, headers=self._headers(), json=payload)
        r.raise_for_status()

    def enviar_nuevo(self, destinatario: str, asunto: str, cuerpo_html: str) -> None:
        """Envía un correo nuevo (no como respuesta)."""
        url = f"{GRAPH}/users/{self.buzon}/sendMail"
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

    def marcar_procesado(self, message_id: str, categorias: list[str] | None = None) -> None:
        """
        Agrega la categoría 'AgenteProcesado' al correo más las categorías de las reglas.
        Así el agente no lo vuelve a procesar en el próximo ciclo.
        """
        todas = [CATEGORIA_PROCESADO] + [c for c in (categorias or []) if c != CATEGORIA_PROCESADO]
        url = f"{GRAPH}/users/{self.buzon}/messages/{message_id}"
        payload = {"categories": todas}
        r = requests.patch(url, headers=self._headers(), json=payload)
        r.raise_for_status()

    def marcar_leido(self, message_id: str) -> None:
        url = f"{GRAPH}/users/{self.buzon}/messages/{message_id}"
        r = requests.patch(url, headers=self._headers(), json={"isRead": True})
        r.raise_for_status()

    # ── Carpetas ──────────────────────────────────────────────────

    def _get_or_create_folder(self, nombre: str) -> str:
        """Devuelve el ID de la carpeta, creándola si no existe. Cachea el resultado."""
        if nombre in self._folder_cache:
            return self._folder_cache[nombre]

        url = f"{GRAPH}/users/{self.buzon}/mailFolders"
        r = requests.get(url, headers=self._headers(), params={"$filter": f"displayName eq '{nombre}'"})
        r.raise_for_status()
        carpetas = r.json().get("value", [])

        if carpetas:
            folder_id = carpetas[0]["id"]
        else:
            r = requests.post(url, headers=self._headers(), json={"displayName": nombre})
            r.raise_for_status()
            folder_id = r.json()["id"]

        self._folder_cache[nombre] = folder_id
        return folder_id

    def mover_a_carpeta(self, message_id: str, nombre_carpeta: str) -> None:
        """Mueve el correo a la carpeta indicada, creándola si no existe."""
        folder_id = self._get_or_create_folder(nombre_carpeta)
        url = f"{GRAPH}/users/{self.buzon}/messages/{message_id}/move"
        r = requests.post(url, headers=self._headers(), json={"destinationId": folder_id})
        r.raise_for_status()

    # ── Escalación ────────────────────────────────────────────────

    def enviar_alerta_escalacion(
        self,
        correo_original: dict,
        red_flags: list[str],
        destinatarios: list[str],
    ) -> None:
        """Envía un email de alerta a los contactos de escalación por red flags detectados."""
        remitente    = correo_original.get("from", {}).get("emailAddress", {}).get("address", "desconocido")
        asunto       = correo_original.get("subject", "(sin asunto)")
        cuerpo_orig  = correo_original.get("body", {}).get("content", "")
        flags_html   = "".join(f"<li><b>{f}</b></li>" for f in red_flags)

        cuerpo_html = (
            f"<p>⚠️ El agente de correo detectó <b>señales de alerta</b> en el siguiente correo:</p>"
            f"<ul>{flags_html}</ul>"
            f"<hr>"
            f"<p><b>De:</b> {remitente}<br>"
            f"<b>Asunto:</b> {asunto}</p>"
            f"<blockquote>{cuerpo_orig}</blockquote>"
        )
        asunto_alerta = f"🚨 Red flag detectado: {asunto}"

        for destinatario in destinatarios:
            self.enviar_nuevo(destinatario, asunto_alerta, cuerpo_html)
