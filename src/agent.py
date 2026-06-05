"""
agent.py — Agente principal de Outlook 365
Corre en loop, revisa correos nuevos, los analiza con Claude y ejecuta acciones.

Uso:
    python src/agent.py              # usa src/config/general_rules.md por defecto
    python src/agent.py --interval 5 # revisa cada 5 minutos
"""

import os
import time
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


def ciclo(mail_client: MailClient, analizador: AnalizadorClaude):
    """Un ciclo completo para un buzón: leer → analizar → actuar."""
    log.info(f"▶ Revisando correos de {mail_client.buzon}...")

    # Lee correos no procesados (sin la categoría 'AgenteProcesado')
    max_correos = int(os.getenv("MAX_CORREOS_POR_CICLO", 20))
    correos = mail_client.leer_no_procesados(cantidad=max_correos)

    if not correos:
        log.info("  Sin correos nuevos.")
        return

    log.info(f"  {len(correos)} correo(s) encontrado(s).")

    for correo in correos:
        try:
            log.info(f"  📧 Procesando: '{correo['subject']}' de {correo['from']['emailAddress']['address']}")

            # Agrega y resuelve el campo custom 'direction' (recibido vs enviado).
            remitente = correo.get("from", {}).get("emailAddress", {}).get("address", "")
            direction = 1 if remitente.lower() == mail_client.buzon.lower() else 0  # 0=recibido, 1=enviado
            correo["direction"] = direction

            # 1. Claude analiza el correo y decide qué hacer
            decision = analizador.analizar(correo, mail_client.buzon)

            log.info(f"  🤖 Decisión: {decision['accion']} — {decision['razon']}")

            # 2. Ejecutar la acción decidida
            if decision["accion"] != "ignorar":
                ejecutar_accion(decision, correo, mail_client)

            # 3. Marcar como procesado (agregar categoría en Outlook)
            mail_client.marcar_procesado(correo["id"])

        except Exception as e:
            log.error(f"  ❌ Error procesando correo {correo['id']}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Agente Outlook 365")
    parser.add_argument("--interval", type=int, default=None, help="Intervalo en minutos")
    parser.add_argument("--config", default=None, help="Carpeta de reglas (default: src/config/)")
    parser.add_argument("--once", action="store_true", help="Correr solo una vez y salir")
    args = parser.parse_args()

    intervalo  = args.interval or int(os.getenv("INTERVALO_MINUTOS", 10))
    buzones    = [b.strip() for b in os.getenv("BUZONES", "").split(";") if b.strip()]
    analizador = AnalizadorClaude(rules_dir=args.config) if args.config else AnalizadorClaude()

    log.info("=" * 55)
    log.info("  Agente Outlook 365 iniciado")
    log.info(f"  Buzones: {', '.join(buzones)}")
    log.info(f"  Intervalo: cada {intervalo} minutos")
    log.info(f"  Reglas: {analizador.rules_dir}")
    log.info("=" * 55)

    if args.once:
        for buzon in buzones:
            ciclo(MailClient(buzon), analizador)
        return

    while True:
        try:
            for buzon in buzones:
                ciclo(MailClient(buzon), analizador)

        except Exception as e:
            log.error(f"Error en ciclo principal: {e}")

        log.info(f"  ⏳ Próxima revisión en {intervalo} minutos...")
        time.sleep(intervalo * 60)


if __name__ == "__main__":
    main()
