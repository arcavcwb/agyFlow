---
name: agy-frontend-delivery
description: Implementar una tarea de interfaz para el Frontend de agyFlow a partir de contratos y diseño revisados, seleccionando procedimientos para Astro, React o Next.js según el proyecto.
---

# Entrega de interfaz

Las rutas mencionadas son relativas a la raíz del proyecto receptor.
Aplicá `docs/protocolo.md`; obtené stack, versiones y rutas de la arquitectura
y de los manifiestos reales dentro de tu alcance.

## Procedimiento

1. Asociá los criterios del ticket a vistas, estados e interacciones existentes.
   Registrá revisión y rutas de contratos y tokens que consume cada cambio.
   Si una dependencia no aplica, explicá por qué; si falta, aislá la parte
   dependiente y continuá solo trabajo independiente dentro del alcance.
2. Leé los schemas existentes en `packages/contracts` o la ruta que declare
   la arquitectura. Reutilizá tipos y validación; no crees contratos paralelos
   ni endpoints de ejemplo para simular una API aún no definida.
3. Elegí el procedimiento técnico por aplicación. En Astro, comprobá el
   renderizado y las integraciones usadas antes de añadir islas interactivas.
   En React, seguí la composición y gestión de estado del proyecto. En Next.js,
   comprobá router, versión y límites de ejecución antes de ubicar datos o estado.
4. Implementá los estados acordados y los errores definidos por el contrato.
   Reutilizá tokens y componentes visuales; documentá cualquier dato o estado
   no cubierto para que su dueño resuelva la dependencia.
5. Seleccioná comprobaciones por comportamiento cambiado: navegación, envío,
   teclado, foco o tamaños de pantalla. Usá comandos y herramientas existentes;
   diferenciá comprobaciones automáticas, manuales y no ejecutadas.
6. Antes de entregar, contrastá las revisiones consumidas con las últimas
   entregas de sus dueños. Si cambiaron, revalidá el comportamiento afectado.

## Ejemplo de límite de contrato

Si el diseño requiere un campo que el schema no define, describí la diferencia
y el estado bloqueado al Backend y al coordinador. No agregues un tipo local
para hacer pasar el chequeo: ese cambio ocultaría la dependencia sin resolverla.

Entregá rutas modificadas, revisiones consumidas, comandos y resultados.
Las skills específicas del framework complementan estas decisiones solo para
la aplicación y versión confirmadas; esta skill no cambia el stack existente.
