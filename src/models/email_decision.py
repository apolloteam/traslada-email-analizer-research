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

    categorias: list[str] = []
    """Categorías de Outlook a asignar. Solo las definidas explícitamente en las reglas que aplican."""

    carpeta_archivo: Optional[str] = None
    """Nombre de la carpeta de Outlook a la que mover el correo al cerrar la conversación. None = no mover."""

    responder_como_draft: bool = False
    """Si es True, la respuesta se guarda como borrador en lugar de enviarse directamente."""

    red_flags_detectados: list[str] = []
    """Nombres de los red flags detectados. Vacío si ninguno aplica."""

    escalar_a: list[str] = []
    """Emails a notificar por escalación (union de todos los red flags que aplican, sin duplicados)."""
