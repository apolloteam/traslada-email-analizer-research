# Agente Outlook 365 con Claude

Agente autónomo que lee correos de Outlook 365, los analiza con Claude y toma acciones automáticamente (responder, reenviar) según las reglas definidas en `config/rules.json`.

---

## Estructura

```
outlook-agent/
├── agent.py          ← Punto de entrada principal (loop principal)
├── mail_client.py    ← Comunicación con Outlook via Graph API
├── analyzer.py       ← Análisis de correos con Claude
├── actions.py        ← Ejecución de respuestas y reenvíos
├── requirements.txt
├── .env.example      ← Copiar a .env y completar con tus credenciales
├── config/
│   └── rules.json    ← ACÁ configurás el comportamiento del agente
└── logs/
    └── agent.log     ← Log de todo lo que hace el agente
```

---

## Setup inicial

### 1. Clonar y crear entorno virtual

```bash
cd outlook-agent
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configurar credenciales

```bash
cp .env.example .env
# Editar .env con tus datos reales
```

### 3. Registrar la app en Azure AD (solo una vez)

1. Ir a portal.azure.com → Azure Active Directory → Registros de aplicaciones
2. Nueva registro → Anotar `CLIENT_ID` y `TENANT_ID`
3. Certificados y secretos → Crear secreto → Anotar `CLIENT_SECRET`
4. Permisos de API → Microsoft Graph → Permisos de aplicación:
   - `Mail.Read`
   - `Mail.Send`
   - `Mail.ReadWrite` (para agregar categorías)
5. Conceder consentimiento de administrador

### 4. Configurar las reglas

Editá `config/rules.json`. Cada regla tiene:

```json
{
  "id": "nombre-unico",
  "descripcion": "Para qué sirve esta regla",
  "condiciones": "Descripción en lenguaje natural de cuándo aplica",
  "accion": "responder | reenviar | responder_y_reenviar | ignorar",
  "reenviar_a": ["email@empresa.com"],
  "instruccion_respuesta": "Qué debe decir la respuesta automática",
  "comentario_reenvio": "Nota que acompaña el reenvío"
}
```

---

## Correr el agente

```bash
# Modo normal (loop cada 10 minutos según config)
python agent.py

# Especificar intervalo
python agent.py --interval 5

# Correr solo una vez (útil para probar)
python agent.py --once

# Usar un archivo de reglas alternativo
python agent.py --config config/rules_noche.json
```

---

## Correr como servicio en Windows (siempre activo)

### Opción A: Task Scheduler (recomendado para servidores Windows)

1. Abrir Task Scheduler → "Create Basic Task"
2. Trigger: "When the computer starts"
3. Action: `python C:\ruta\outlook-agent\agent.py`
4. Marcar "Run whether user is logged on or not"

### Opción B: Script de instalación como servicio (con NSSM)

```bash
# Descargar NSSM desde https://nssm.cc
nssm install OutlookAgente "C:\ruta\.venv\Scripts\python.exe" "C:\ruta\agent.py"
nssm set OutlookAgente AppDirectory "C:\ruta\outlook-agent"
nssm start OutlookAgente
```

### En Linux/Mac (systemd)

Crear `/etc/systemd/system/outlook-agente.service`:

```ini
[Unit]
Description=Agente Outlook 365
After=network.target

[Service]
Type=simple
User=tu_usuario
WorkingDirectory=/ruta/outlook-agent
ExecStart=/ruta/outlook-agent/.venv/bin/python agent.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable outlook-agente
sudo systemctl start outlook-agente
sudo systemctl status outlook-agente
```

---

## Ver los logs

```bash
# En tiempo real
tail -f logs/agent.log

# En Windows (PowerShell)
Get-Content logs\agent.log -Wait
```

---

## Cómo funciona el ciclo

```
Cada X minutos:
  1. Leer correos sin categoría "AgenteProcesado"
  2. Para cada correo:
     a. Claude analiza el texto + reglas del rules.json
     b. Claude decide: responder / reenviar / ambos / ignorar
     c. Se ejecuta la acción
     d. Se marca el correo como "AgenteProcesado" (no se vuelve a procesar)
  3. Esperar hasta el próximo ciclo
```

---

## Agregar nuevas reglas

Solo editás `config/rules.json` — no hace falta tocar código. El agente levanta las reglas en cada ciclo, así que los cambios aplican de inmediato sin reiniciar.
