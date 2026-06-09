# Traslada - Agente AI de buzones de correo
Guía para redactar reglas de buzón de correo electrónico.

## ¿Para qué sirve este archivo?

Cada buzón de correo del sistema tiene su propio archivo de reglas (por ejemplo, para **ventas**@traslada.com.ar => **ventas**_rules.md). Este archivo de reglas le explica al agente de inteligencia artificial **cómo comportarse** cuando procesa los correos de ese buzón específico.

El agente lee este archivo antes de analizar cada correo y lo usa para decidir:
- Qué buzón de correo está analizando.
- Qué hacer con el correo entrante (responder, reenviar, ignorar).
- Qué tono usar en la respuesta.
- Qué categoría (etiqueta) agregarle.
- Dónde archivar el correo cuando la conversación termina.

> ⚠️ **Importante:** El agente sigue estas instrucciones al pie de la letra. Si algo no está escrito acá, el agente no lo va a hacer. Si algo está mal escrito o es ambiguo, puede tomar decisiones incorrectas.

---

## Estructura del archivo

El archivo debe estar en formato [Markdown](https://www.markdownguide.org/cheat-sheet/).

Un archivo de reglas tiene hasta cuatro partes, en este orden:

```
1. Encabezado del buzón   → quién es y para qué sirve este buzón
2. Tono específico        → cómo hablar en este buzón (opcional)
3. Reglas                 → qué hacer con cada tipo de correo
4. Archivo de correos     → cuándo y dónde guardar conversaciones cerradas
```

---

## Parte 1 — Encabezado del buzón

Es la primera línea del archivo. Le dice al agente de qué buzón se trata y cuál es su propósito.

```markdown
Reglas y consideraciones para este buzón.
**Buzón:** ventas@traslada.com.ar
**Propósito:** Recibe consultas comerciales, leads, y primeros contactos de clientes potenciales.
```

**¿Por qué importa?** El agente usa el propósito del buzón como contexto general para tomar decisiones en casos que no están cubiertos por ninguna regla específica.

---

## Parte 2 — Tono específico (opcional)

Si el buzón necesita un tono diferente al estándar de la empresa, acá se define. Si no se incluye esta sección, el agente usa el tono empresarial general.

```markdown
## Tono para este buzón

Complementa el tono base con:
- Entusiasta y orientado a la oportunidad: el cliente potencial está considerando
  contratarnos, tratalo como si fuera una venta que queremos ganar.
- Usá el nombre del remitente si figura en el correo.
- Evitá tecnicismos de logística — hablá en términos del beneficio para el cliente.
```

**Consejos:**
- Podés decir "Complementa el tono base con..." si solo querés agregar matices.
- O "Reemplaza el tono base:" si el buzón necesita un estilo muy diferente (por ejemplo, un buzón interno para choferes donde el tono es más directo e informal).

---

## Parte 3 — Reglas

Esta es la parte más importante. Cada regla le dice al agente qué hacer cuando recibe un tipo específico de correo.

### Estructura de una regla

```markdown
## Nombre de la regla

**condiciones:** Descripción de cuándo aplica esta regla.

Ejemplos que aplican: "frase de ejemplo 1", "frase de ejemplo 2".
No aplica si: descripción de casos que parecen similares pero no corresponden.

- `accion`: qué hacer (responder, enviar, responder y reenviar, omitir)
- `reenviar_a`: a quién reenviar
- `instruccion_respuesta`: qué decir en la respuesta
- `comentario_reenvio`: nota interna que acompaña el reenvío
- `categorias`: etiquetas de Outlook
- `borrador`: si la respuesta debe quedar en borrador antes de enviar
```

Veamos cada campo en detalle.

---

### Campo: `accion` (obligatorio)

**¿Qué hace?** Le indica al agente qué acción ejecutar.

**Valores posibles:**

| Valor | Qué hace |
|---|---|
| `responder` | Envía una respuesta al remitente |
| `reenviar` | Reenvía el correo a alguien interno, sin responder al cliente |
| `responder_y_reenviar` | Responde al cliente Y reenvía internamente |
| `ignorar` | No hace nada (pero puede categorizar y archivar igual) |

**Ejemplo:**
```markdown
- `accion`: responder_y_reenviar
```

---

### Campo: `reenviar_a`

**¿Qué hace?** Lista de emails internos a los que se reenvía el correo. Solo se usa cuando la acción incluye `reenviar`.

**Ejemplo con uno:**
```markdown
- `reenviar_a`: juan@traslada.com.ar
```

**Ejemplo con varios:**
```markdown
- `reenviar_a`: juan@traslada.com.ar, maria@traslada.com.ar
```

---

### Campo: `instruccion_respuesta`

**¿Qué hace?** Le dice al agente *qué escribir* en la respuesta al cliente. No es el texto final — es una instrucción que el agente interpreta para redactar la respuesta. Solo se usa cuando la acción incluye `responder`.

**Consejos para redactarlo bien:**
- Sé específico sobre qué información incluir y cuál no.
- Indicá el tono si es diferente al habitual para este caso puntual.
- Si no querés que prometa algo, decilo explícitamente.

**Ejemplo simple:**
```markdown
- `instruccion_respuesta`: Agradecé el contacto e indicá que un asesor se comunicará a la brevedad.
```

**Ejemplo detallado:**
```markdown
- `instruccion_respuesta`: Pedí disculpas sinceras por la experiencia negativa. Indicá
  que escalaste el caso y que alguien de atención al cliente se contactará en las
  próximas 2 horas. No prometás soluciones específicas todavía.
```

---

### Campo: `comentario_reenvio`

**¿Qué hace?** Texto que se agrega al principio del correo reenviado, a modo de nota interna para quien lo recibe. Solo aplica cuando la acción incluye `reenviar`.

**Ejemplo:**
```markdown
- `comentario_reenvio`: 💼 Lead comercial entrante. Contactar a la brevedad.
```

> 💡 Tip: Podés usar emojis para que sea más fácil de identificar visualmente en la bandeja de entrada de quien lo recibe.

---

### Campo: `categorias`

**¿Qué hace?** Lista de etiquetas que se asignan al correo en Outlook. Sirven para filtrar, buscar y organizar correos visualmente.

**Formato:**
```markdown
- `categorias`: ["NombreEtiqueta1", "NombreEtiqueta2"]
```

**Ejemplo:**
```markdown
- `categorias`: ["Comercial", "Lead"]
```

> ⚠️ **Importante:** Las categorías que ponés acá deben existir previamente en Outlook, o el administrador del sistema debe crearlas. Si ponés una categoría que no existe, el agente la va a ignorar.

---

### Campo: `borrador`

**¿Qué hace?** Si es `true`, la respuesta al cliente **no se envía automáticamente** — queda guardada como borrador en Outlook para que una persona la revise y envíe manualmente. Muy útil para respuestas delicadas.

**Ejemplo:**
```markdown
- `borrador`: true
```

Si no se incluye este campo, la respuesta se envía automáticamente.

---

## Ejemplo de regla simple

Una regla que solo reenvía, sin responder al cliente:

```markdown
## Facturación y administración

**condiciones:** El correo menciona facturas, pagos, transferencias, comprobantes,
o consultas administrativas.

Ejemplos que aplican: "adjunto la factura", "necesito el comprobante de pago",
"¿puedo pagar en cuotas?".

- `accion`: reenviar
- `reenviar_a`: administracion@traslada.com.ar
- `comentario_reenvio`: 📄 Consulta de facturación — derivada automáticamente.
```

---

## Ejemplo de regla completa (todos los campos)

```markdown
## Consulta comercial

**condiciones:** El correo pregunta por precios, cotizaciones, presupuestos,
o expresa interés en adquirir productos o servicios.

Ejemplos que aplican: "¿cuánto cuesta?", "necesito un presupuesto",
"quiero contratar", "me interesa el servicio".
No aplica si ya es un cliente existente con una queja o problema técnico.

- `accion`: responder_y_reenviar
- `reenviar_a`: ventas@traslada.com.ar
- `instruccion_respuesta`: Agradecé el interés con entusiasmo. Informá que un asesor
  comercial se contactará en breve con una propuesta personalizada. Si figura el
  nombre de la empresa en el correo, mencionala. No detalles precios ni condiciones.
- `comentario_reenvio`: 💼 Lead comercial entrante. Contactar a la brevedad.
- `categorias`: ["Comercial", "Lead"]
- `borrador`: true
```

---

## Parte 4 — Archivo de conversaciones finalizadas

Esta sección le dice al agente cuándo considerar que una conversación terminó y a qué carpeta de Outlook moverla.

```markdown
## Archivo de conversaciones finalizadas

Cuando determinés que la conversación está completamente resuelta (el cliente
agradeció, confirmó conformidad, o el tema claramente no requiere seguimiento),
asigná `carpeta_archivo` con la carpeta correspondiente:

- El cliente aceptó un presupuesto o contrató el servicio → `"Comercial/Cerrado"`
- La solicitud fue rechazada o no aplica → `"Comercial/NoAtendible"`
- El reclamo fue resuelto y el cliente confirmó conformidad → `"Reclamos/Resuelto"`

Si la conversación sigue abierta, el cliente no respondió, o hay dudas
→ dejá `carpeta_archivo` en null (no mover).
```

**¿Qué pasa si la carpeta no existe en Outlook?** El sistema la crea automáticamente, incluyendo subcarpetas (por ejemplo `"Comercial/Cerrado"` crea la carpeta `Comercial` con la subcarpeta `Cerrado` adentro).

---

## Ejemplo completo de un archivo de buzón

Así quedaría un archivo `ventas_rules.md` completo y listo para usar:

```markdown
Reglas y consideraciones para este buzón.
**Buzón:** ventas@traslada.com.ar
**Propósito:** Recibe consultas comerciales, leads, y primeros contactos de clientes potenciales.

## Tono para este buzón

Complementa el tono base con:
- Entusiasta y orientado a la oportunidad: el cliente potencial está considerando
  contratarnos, tratalo como si fuera una venta que queremos ganar.
- Usá el nombre del remitente si figura en el correo.
- Evitá tecnicismos de logística — hablá en términos del beneficio para el cliente.


## Consulta comercial

**condiciones:** El correo pregunta por precios, cotizaciones, presupuestos,
o expresa interés en adquirir productos o servicios.

Ejemplos que aplican: "¿cuánto cuesta?", "necesito un presupuesto",
"quiero contratar", "me interesa el servicio".
No aplica si ya es un cliente existente con una queja o problema técnico.

- `accion`: responder_y_reenviar
- `reenviar_a`: ventas@traslada.com.ar
- `instruccion_respuesta`: Agradecé el interés con entusiasmo. Informá que un asesor
  comercial se contactará en breve con una propuesta personalizada. Si figura el
  nombre de la empresa en el correo, mencionala. No detalles precios ni condiciones.
- `comentario_reenvio`: 💼 Lead comercial entrante. Contactar a la brevedad.
- `categorias`: ["Comercial", "Lead"]
- `borrador`: true


## Reclamo de cliente

**condiciones:** El correo expresa insatisfacción, reclamo, queja, o menciona
palabras como "mal servicio", "decepcionado", "exijo", "no funciona".

Ejemplos que aplican: "estoy muy disconforme", "exijo una solución",
"el servicio fue un desastre", "nunca me respondieron".
No aplica si es un reporte técnico puntual sin tono de queja.

- `accion`: responder_y_reenviar
- `reenviar_a`: atencion@traslada.com.ar
- `instruccion_respuesta`: Pedí disculpas sinceras por la experiencia negativa.
  Indicá que escalaste el caso y que alguien se contactará en las próximas 2 horas.
  No prometás soluciones específicas todavía.
- `comentario_reenvio`: 🚨 RECLAMO DE CLIENTE — Requiere atención prioritaria.
- `categorias`: ["Reclamo"]
- `borrador`: true


## Facturación y administración

**condiciones:** El correo menciona facturas, pagos, transferencias, comprobantes,
o consultas administrativas.

Ejemplos que aplican: "adjunto la factura", "necesito el comprobante de pago",
"¿puedo pagar en cuotas?".

- `accion`: reenviar
- `reenviar_a`: administracion@traslada.com.ar
- `comentario_reenvio`: 📄 Consulta de facturación — derivada automáticamente.


## Archivo de conversaciones finalizadas

Cuando determinés que la conversación está completamente resuelta (el cliente
agradeció, confirmó conformidad, o el tema claramente no requiere seguimiento),
asigná `carpeta_archivo` con la carpeta correspondiente:

- El cliente aceptó un presupuesto o contrató el servicio → `"Comercial/Cerrado"`
- La solicitud fue rechazada o no aplica → `"Comercial/NoAtendible"`
- El reclamo fue resuelto y el cliente confirmó conformidad → `"Reclamos/Resuelto"`
- Consulta de facturación resuelta → `"Administracion/Resuelto"`

Si la conversación sigue abierta, el cliente no respondió, o hay dudas
→ dejá `carpeta_archivo` en null (no mover).
```

---

## Preguntas frecuentes

**¿Qué pasa si un correo no coincide con ninguna regla?**
El agente usa la regla "Respuesta automática general" que está en las reglas generales de la empresa. Si esa tampoco aplica, el correo se ignora.

**¿Qué pasa si un correo coincide con más de una regla?**
El agente aplica la regla más específica. Por eso es importante que cada regla tenga bien definido el "No aplica si...".

**¿Puedo tener tantas reglas como quiera?**
Sí, pero cuantas más reglas haya, más posibilidades hay de que se superpongan. Mantené las reglas claras y con buenos ejemplos de qué sí y qué no aplica.

**¿El agente puede inventar categorías que no están en las reglas?**
No. Solo puede usar las categorías que estén escritas explícitamente en las reglas que aplican al correo.

**¿Puedo usar emojis en los nombres de categorías?**
Sí, como `"⭐ Prioritario"` o `"📦 Logística"`. Ayudan a identificarlas visualmente en Outlook.

**¿Puedo asignarle un color a las categorías desde las reglas?**
No. El sistema puede crear la categoría en Outlook automáticamente, pero el color solo se puede asignar manualmente desde el cliente de Outlook (clic derecho sobre la categoría → Cambiar color). Es un paso que hay que hacer una sola vez por categoría nueva.