from pydantic import BaseModel
from typing import Optional


class EmailDecision(BaseModel):
    """
    Modelo de salida estructurada que representa la decisión del agente sobre un correo electrónico 
    analizado.
    """

    accion: str
    """Acción a ejecutar: 'responder' | 'reenviar' | 'responder_y_reenviar' | 'ignorar'."""

    razon: str
    """Explicación breve de por qué se tomó esta decisión."""

    respuesta_html: Optional[str] = None
    """Cuerpo HTML de la respuesta. Presente solo cuando accion incluye 'responder'."""

    reenviar_a: list[str] = []
    """Lista de emails destino. Presente solo cuando accion incluye 'reenviar'."""

    comentario_reenvio: Optional[str] = None
    """Texto opcional que acompaña el reenvío."""

    prioridad: str
    """Prioridad del correo: 'alta' | 'media' | 'baja'."""

    categories: list[str] = []
    """Categorías de Outlook a asignar. Solo las definidas explícitamente en las reglas que aplican."""
