"""
actions.py — Ejecuta las acciones decididas por Claude.
"""

import logging
from mail_client import MailClient

log = logging.getLogger(__name__)


def ejecutar_accion(decision: dict, correo: dict, mail: MailClient) -> None:
    """
    Recibe la decisión de Claude y ejecuta la acción correspondiente.

    Acciones posibles:
      - responder              → responde al remitente original
      - reenviar               → reenvía a uno o más destinatarios del equipo
      - responder_y_reenviar   → hace ambas cosas
      - ignorar                → no hace nada (ya filtrado antes de llegar aquí)
    """
    accion     = decision.get("accion", "ignorar")
    remitente  = correo["from"]["emailAddress"]["address"]
    asunto     = correo.get("subject", "(sin asunto)")
    msg_id     = correo["id"]

    if accion == "responder":
        _responder(mail, msg_id, remitente, asunto, decision)

    elif accion == "reenviar":
        _reenviar(mail, msg_id, decision)

    elif accion == "responder_y_reenviar":
        _responder(mail, msg_id, remitente, asunto, decision)
        _reenviar(mail, msg_id, decision)

    else:
        log.info(f"    → Acción: ignorar (sin operación)")


def _responder(mail: MailClient, msg_id: str, remitente: str, asunto: str, decision: dict):
    cuerpo = decision.get("respuesta_html")
    if not cuerpo:
        log.warning("    ⚠️  Acción 'responder' sin respuesta_html. Saltando.")
        return

    if decision.get("responder_como_draft", False):
        mail.crear_draft_respuesta(msg_id, cuerpo)
        log.info(f"    📝  Borrador creado para: {remitente} | Asunto: {asunto}")
    else:
        mail.responder(msg_id, cuerpo)
        log.info(f"    ✉️  Respuesta enviada a: {remitente} | Asunto: {asunto}")


def _reenviar(mail: MailClient, msg_id: str, decision: dict):
    destinatarios = decision.get("reenviar_a", [])
    if not destinatarios:
        log.warning("    ⚠️  Acción 'reenviar' sin destinatarios. Saltando.")
        return

    comentario = decision.get("comentario_reenvio", "")
    mail.reenviar(msg_id, destinatarios, comentario)
    log.info(f"    ↪️  Reenviado a: {', '.join(destinatarios)}")
