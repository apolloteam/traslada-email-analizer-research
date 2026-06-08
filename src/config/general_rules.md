## Red Flags

### Amenaza legal
**condiciones:** El correo menciona abogados, demandas, juicio, "voy a denunciar", acciones legales, mediación, o cualquier lenguaje que implique una acción legal contra la empresa.

- `escalar_a`: estebansomma@traslada.com.ar
- `categories`: ["🚨 Red Flag", "Legal"]

### Mención de prensa o redes sociales
**condiciones:** El cliente amenaza con publicar su experiencia en redes sociales, contactar medios de comunicación, hacer pública su queja, o menciona periodistas.

- `escalar_a`: estebansomma@traslada.com.ar
- `categories`: ["🚨 Red Flag", "Reputacional"]


## Soporte técnico

**condiciones:** El correo menciona errores, fallas, sistemas caídos, bugs, o problemas técnicos.

Ejemplos que aplican: "el sistema no carga", "me da error 500", "la app se cayó", "no puedo acceder al portal".
No aplica si es una consulta de uso ("¿cómo hago X?") o una sugerencia de mejora.

- `accion`: responder_y_reenviar
- `reenviar_a`: estebansomma@traslada.com.ar
- `instruccion_respuesta`: Confirmá la recepción del reporte, indicá que el equipo técnico fue notificado y que responderán en un máximo de 4 horas hábiles. Sé profesional y empático.
- `comentario_reenvio`: ⚠️ Incidente técnico reportado por cliente. Requiere atención.
- `categories`: ["Soporte", "Incidente"]


## Respuesta automática general

**condiciones:** Cualquier correo que no encaje en las reglas anteriores y sea de un remitente externo.

No aplica a correos internos del dominio traslada.com.ar.

- `accion`: responder
- `instruccion_respuesta`: Agradecé el contacto. Indicá que el horario de atención es de lunes a viernes de 9 a 18 hs. Que revisarán su mensaje y responderán a la brevedad. No detalles más información.
- `categories`: ["Ignorar"]
