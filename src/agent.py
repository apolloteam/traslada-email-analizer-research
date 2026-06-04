"""
agent.py — Agente principal de Outlook 365
Corre en loop, revisa correos nuevos, los analiza con Claude y ejecuta acciones.

Uso:
    python src/agent.py              # usa src/config/rules.json por defecto
    python src/agent.py --interval 5 # revisa cada 5 minutos
"""

import os
import time
import json
import logging
import argparse
from datetime import datetime, timezone

_DIR = os.path.dirname(os.path.abspath(__file__))

from mail_client import MailClient 
from analyzer import AnalizadorClaude
from actions import ejecutar_accion

# ── Logging ────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(_DIR, "logs", "agent.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


def cargar_config(path: str = os.path.join(_DIR, "config", "rules.json")) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def ciclo(mail: MailClient, analizador: AnalizadorClaude, config: dict):
    """Un ciclo completo: leer → analizar → actuar."""
    log.info("▶ Revisando correos nuevos...")

    correos = mail.leer_no_procesados(cantidad=config.get("max_correos_por_ciclo", 20))

    if not correos:
        log.info("  Sin correos nuevos.")
        return

    log.info(f"  {len(correos)} correo(s) encontrado(s).")

    for correo in correos:
        try:
            log.info(f"  📧 Procesando: '{correo['subject']}' de {correo['from']['emailAddress']['address']}")

            # Agrega y resuelve el campo custom 'direction' (recibido vs enviado).
            remitente = correo.get("from", {}).get("emailAddress", {}).get("address", "")
            direction = 1 if remitente.lower() == mail.user_email.lower() else 0  # 0=recibido, 1=enviado
            correo["direction"] = direction

            # 1. Claude analiza el correo y decide qué hacer
            decision = analizador.analizar(correo, config["reglas"])

            log.info(f"  🤖 Decisión: {decision['accion']} — {decision['razon']}")

            # 2. Ejecutar la acción decidida
            if decision["accion"] != "ignorar":
                ejecutar_accion(decision, correo, mail, config)

            # 3. Marcar como procesado (agregar categoría en Outlook)
            mail.marcar_procesado(correo["id"])

        except Exception as e:
            log.error(f"  ❌ Error procesando correo {correo['id']}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Agente Outlook 365")
    parser.add_argument("--interval", type=int, default=None, help="Intervalo en minutos")
    parser.add_argument("--config", default=os.path.join(_DIR, "config", "rules.json"), help="Ruta al archivo de reglas")
    parser.add_argument("--once", action="store_true", help="Correr solo una vez y salir")
    args = parser.parse_args()

    config = cargar_config(args.config)
    intervalo = args.interval or config.get("intervalo_minutos", 10)

    mail      = MailClient()
    analizador = AnalizadorClaude()

    log.info("=" * 55)
    log.info("  Agente Outlook 365 iniciado")
    log.info(f"  Intervalo: cada {intervalo} minutos")
    log.info(f"  Config: {args.config}")
    log.info("=" * 55)

    if args.once:
        ciclo(mail, analizador, config)
        return

    while True:
        try:
            ciclo(mail, analizador, config)
        except Exception as e:
            log.error(f"Error en ciclo principal: {e}")

        log.info(f"  ⏳ Próxima revisión en {intervalo} minutos...")
        time.sleep(intervalo * 60)


if __name__ == "__main__":
    main()
