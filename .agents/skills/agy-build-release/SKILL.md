---
name: agy-build-release
description: Preparar builds y evidencia de Staging para DevOps en agyFlow, comprobando correspondencia entre QA, revisión y artefacto sin asumir proveedor de despliegue.
---

# Build y entrega de Staging

Las rutas mencionadas son relativas a la raíz del proyecto receptor.
Aplicá `docs/protocolo.md`; el destino y procedimiento de despliegue proceden de
`architecture.md` y de la configuración real dentro del alcance asignado.

## Procedimiento

1. Identificá las aplicaciones afectadas y sus comandos de build, runtime y
   salidas reales en manifiestos y CI. Astro, Next.js y servicios Node/NestJS
   pueden requerir artefactos diferentes; no asumas un directorio único de salida.
2. Distinguí preparación de despliegue. Prepará build, CI y entorno asignados
   antes de QA; integrá esa configuración con producto y tests para fijar la
   revisión candidata. Antes de desplegar, asociá QA aprobado a esa revisión
   y comprobá pendientes y cambios posteriores según el protocolo.
3. Reproducí el build con runtime y gestor de paquetes declarados, usando el
   lockfile existente. Un fallo de instalación o configuración no justifica
   actualizar versiones o regenerar dependencias fuera del alcance de la tarea.
4. Identificá el artefacto construido con revisión y huella o ID verificable.
   Conservá comandos, resultados y configuración relevante sin valores secretos.
5. Con un despliegue de Staging autorizado, aplicá el mecanismo existente al
   destino confirmado. Verificá el servicio mediante las comprobaciones definidas
   por el proyecto; no inventes rutas de salud ni supongas éxito por una URL.
6. Si falla el despliegue, distinguí build, publicación e inicio del servicio.
   Conservá diagnóstico y seguí la recuperación documentada; si no existe,
   reportá el bloqueo con el estado observable del artefacto y del destino.
7. Registrá la evidencia en `docs/deployments/`: revisión, referencia QA,
   artefacto, destino, fecha y comprobación posterior o motivo de bloqueo.

## Ejemplo de revisión incompatible

Si QA aprobó una revisión y el árbol incluye cambios posteriores del producto,
identificá la diferencia y solicitá su revalidación por el circuito definido.
Un build exitoso de la revisión nueva no sustituye la evidencia faltante de QA.

Preparar esta evidencia permite revisar una entrega concreta. La aprobación de
producción se aplica al artefacto y destino especificados en el protocolo;
esta skill no la concede ni selecciona servicios externos por su cuenta.
