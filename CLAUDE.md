# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Agente autónomo que lee emails de Outlook 365 via Microsoft Graph API, los analiza con Claude, y ejecuta acciones automáticas (responder, reenviar) según reglas configurables en JSON.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env_example .env   # completar con credenciales reales
```

Variables de entorno requeridas (ver `.env_example`):
- `CLIENT_ID`, `CLIENT_SECRET`, `TENANT_ID` — app registrada en Azure AD con permisos Mail.Read, Mail.Send, Mail.ReadWrite
- `USER_EMAIL` — casilla de Outlook a monitorear
- `ANTHROPIC_API_KEY` — clave de API de Anthropic

## Run Commands

```powershell
python src/agent.py                                    # loop cada 10 minutos
python src/agent.py --once                             # una sola ejecución (útil para pruebas)
python src/agent.py --interval 5                       # loop cada 5 minutos
python src/agent.py --config src/config/rules_noche.json   # reglas alternativas
```

Logs en `src/logs/agent.log`. Para seguir en tiempo real:
```powershell
Get-Content src\logs\agent.log -Wait
```

## Architecture

El flujo principal es: **leer → analizar → actuar → marcar**.

```
src/agent.py          Orquestador del loop. Carga reglas, llama a mail_client,
                      analyzer y actions en secuencia. Argumentos CLI con argparse.

src/mail_client.py    Wrapper sobre Microsoft Graph API. Autentica via MSAL (OAuth2
                      client_credentials). Filtra emails SIN la categoría
                      "AgenteProcesado" para evitar reprocesamiento. Después de
                      actuar, marca el email con esa categoría.

src/analyzer.py       Integración con Claude. Recibe el texto del email + reglas,
                      devuelve JSON con: accion, razon, respuesta_html, reenviar_a,
                      comentario_reenvio, prioridad. Acciones posibles: responder |
                      reenviar | responder_y_reenviar | ignorar.

src/actions.py        Ejecuta la decisión de Claude delegando en mail_client.
```

**Diseño clave**: las reglas en `src/config/rules.json` se recargan en cada ciclo (hot-reload). Cada regla define condiciones en lenguaje natural que Claude interpreta — no hay parsing de reglas en código. Si Claude falla en un email individual, el error se loguea y el agente continúa con el siguiente.

## Rules Configuration

`src/config/rules.json` define un array de reglas con campos:
- `id`, `descripcion` — identificación
- `condiciones` — texto en lenguaje natural que Claude usa para decidir si aplica
- `accion` — `responder` | `reenviar` | `responder_y_reenviar` | `ignorar`
- `reenviar_a` — lista de emails destino (para acciones con reenvío)
- `instruccion_respuesta` — instrucción para Claude al redactar la respuesta HTML

Se pueden crear archivos alternativos (e.g. `src/config/rules_noche.json`) y pasarlos con `--config`.

## Model in Use

`src/analyzer.py` usa `claude-sonnet-4-6`. Si se cambia de modelo, actualizar la constante en ese archivo.

## Git Commits
Antes de hacer un commit, leer las convenciones en `.claude/docs/commit-conventions.md`.

## Coding Style
- En los `return`, siempre asignar el resultado a una variable y retornar esa variable. Nunca encadenar llamadas directamente en el `return`.
  ✓ `resultado = valor.strip()[:4000]` / `return resultado`
  ✗ `return valor.strip()[:4000]`
