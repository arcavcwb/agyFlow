---
name: agy-design-handoff
description: Preparar una entrega visual verificable para el Designer de agyFlow con referencias, tokens, variantes y estados listos para su implementación.
---

# Entrega visual

Las rutas mencionadas son relativas a la raíz del proyecto receptor.
Aplicá `docs/protocolo.md` y las decisiones visuales de `architecture.md`.
La herramienta de diseño se selecciona en el proyecto, no en esta skill.

## Procedimiento

1. Identificá la referencia visual autorizada y su revisión, archivo o enlace
   verificable. Si participan Figma y Pencil, registrá cuál es la referencia
   principal y cómo se identifica la exportación o copia derivada.
2. Confirmá qué producto llamado Pencil se usa y qué capacidades están
   disponibles antes de elegir un formato o una integración. Una mención del
   nombre no acredita acceso a archivos, MCP ni permisos de escritura.
3. Inventariá componentes y tokens existentes en las rutas visuales asignadas.
   Extendé los que cubran el caso; justificá los nuevos por su uso o variante.
4. Describí estados requeridos por el ticket: inicial, carga, vacío, error,
   interacción y tamaños de pantalla aplicables. Señalá los no especificados
   para resolverlos sin atribuir al producto comportamientos inventados.
5. Entregá valores o referencias concretas para color, tipografía, espacio y
   foco, junto con assets y variantes. Diferenciá decisiones reutilizables de
   ajustes locales para evitar un token global por cada excepción visual.
6. Comprobá legibilidad, contraste e interacción por teclado relevantes para
   la entrega. Si solo evaluaste una captura, no afirmes verificar interacción.
7. Registrá revisión de referencia, rutas entregadas y consumidores. Un cambio
   posterior identifica qué tokens o variantes deben volver a revisarse.

## Ejemplo de entrega

Para una tarjeta, entregá su referencia autorizada, tokens reutilizados,
variante compacta si fue pedida y representación del estado vacío acordado.
Una captura aporta evidencia visual; los tokens y assets concretos permiten
implementar la misma decisión sin adivinar medidas o estados.

Impeccable u otra skill visual complementa este procedimiento si está disponible.
Usar Figma/Pencil para leer una referencia no autoriza publicar cambios remotos.
