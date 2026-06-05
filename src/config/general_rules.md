## Soporte técnico

**condiciones:** El correo menciona errores, fallas, sistemas caídos, bugs, o problemas técnicos.

Ejemplos que aplican: "el sistema no carga", "me da error 500", "la app se cayó", "no puedo acceder al portal".
No aplica si es una consulta de uso ("¿cómo hago X?") o una sugerencia de mejora.

- `accion`: responder_y_reenviar
- `reenviar_a`: estebansomma@traslada.com.ar
- `instruccion_respuesta`: Confirmá la recepción del reporte, indicá que el equipo técnico fue notificado y que responderán en un máximo de 4 horas hábiles. Sé profesional y empático.
- `comentario_reenvio`: ⚠️ Incidente técnico reportado por cliente. Requiere atención.


## Consulta comercial

**condiciones:** El correo pregunta por precios, cotizaciones, presupuestos, o expresa interés en adquirir productos o servicios.

Ejemplos que aplican: "¿cuánto cuesta?", "necesito un presupuesto", "quiero contratar", "me interesa el servicio".
No aplica si ya es un cliente con una queja o un problema técnico.

- `accion`: responder_y_reenviar
- `reenviar_a`: estebansomma@traslada.com.ar
- `instruccion_respuesta`: Agradecé el interés, informá que un asesor comercial se contactará en breve con una propuesta personalizada. Incluí el nombre de la empresa si figura en el correo.
- `comentario_reenvio`: 💼 Lead comercial entrante. Contactar a la brevedad.


## Reclamo de cliente

**condiciones:** El correo expresa insatisfacción, reclamo, queja, o menciona palabras como "mal servicio", "decepcionado", "exijo", "no funciona", "problema con mi pedido".

Ejemplos que aplican: "estoy muy disconforme", "exijo una solución", "el pedido llegó mal", "nunca me respondieron".
No aplica si es un reporte técnico puntual sin tono de queja — esos van a Soporte técnico.

- `accion`: responder_y_reenviar
- `reenviar_a`: estebansomma@traslada.com.ar
- `instruccion_respuesta`: Pedí disculpas sinceras por la experiencia negativa. Indicá que escalaste el caso y que alguien de atención al cliente se contactará en las próximas 2 horas. No prometás soluciones específicas todavía.
- `comentario_reenvio`: 🚨 RECLAMO DE CLIENTE — Requiere atención prioritaria.


## Facturación y administración

**condiciones:** El correo menciona facturas, pagos, transferencias, comprobantes, cuentas corrientes, o administración.

Ejemplos que aplican: "adjunto la factura", "necesito el comprobante de pago", "consulta sobre mi cuenta corriente", "¿puedo pagar en cuotas?".

- `accion`: reenviar
- `reenviar_a`: estebansomma@traslada.com.ar
- `comentario_reenvio`: 📄 Consulta de facturación/administración.


## Respuesta automática general

**condiciones:** Cualquier correo que no encaje en las reglas anteriores y sea de un remitente externo.

No aplica a correos internos del dominio traslada.com.ar.

- `accion`: responder
- `instruccion_respuesta`: Agradecé el contacto. Indicá que el horario de atención es de lunes a viernes de 9 a 18 hs. Que revisarán su mensaje y responderán a la brevedad. No detalles más información.
