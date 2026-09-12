---
name: agy-qa-evidence
description: Evaluar criterios de aceptación y emitir evidencia de QA para una revisión concreta en agyFlow, incluidos dictámenes rechazados o bloqueados.
---

# QA con evidencia identificable

Las rutas mencionadas son relativas a la raíz del proyecto receptor.
Aplicá `docs/protocolo.md`; usá `templates/bug_report.md` para iniciar el reporte.
El resultado pertenece a una revisión del producto y a una ejecución concreta.

## Procedimiento

Antes de la ejecución final, prepará tests y configuración en rutas asignadas.
Coordiná manifests y lockfiles con su escritor. Fijá la revisión candidata después
de integrar producto, pruebas y configuración; preparar pruebas no es aprobar QA.

1. Identificá ticket, historia, criterios, revisión del producto y de los tests,
   entorno e ID de ejecución antes de probar. Comprobá que el entorno ejecuta
   esa revisión; si no puede verificarse, registrá la limitación y su bloqueo.
2. Relacioná cada criterio con una comprobación observable. Elegí el nivel más
   directo: contrato o servicio para reglas de datos, integración para su unión,
   navegador para interacción. No dupliques pruebas solo para aumentar cantidad.
3. Ejecutá las comprobaciones pertinentes con datos autorizados. Registrá
   comandos o pasos, resultados y archivos o enlaces de evidencia sin secretos.
4. Para un fallo, reducí la reproducción hasta conservar su causa observable.
   Describí esperado frente a observado y severidad según impacto del criterio;
   una hipótesis de causa no se presenta como causa demostrada.
5. Emití siempre `bug_report.md`, incluso si no se pudo ejecutar ninguna prueba.
   Conservá historial y señalá claramente qué resultado está vigente para cada
   ticket/revisión. No reutilices un aprobado de otro commit como resultado actual.
6. Dictaminá aprobado solo con los criterios obligatorios verificados y sin
   bloqueantes. Dictaminá rechazado ante un fallo demostrado; si además faltan
   pruebas, dejá su alcance pendiente. Sin evidencia suficiente para aceptar ni
   fallos demostrados, dictaminá bloqueado y explicá qué falta para continuar.

## Ejemplo de evidencia insuficiente

Si el navegador no inicia, registrá el comando y su error, entorno y criterios
no ejecutados. “No encontré bugs” no describe ese resultado: el dictamen es
bloqueado. Si un test sí demostró un fallo, preservá también esa evidencia.

Entregá todos los dictámenes al responsable de estado operativo del sprint:
Scrum manual o Automation, con responsables propuestos para los fallos.
Las reaperturas y el estado remoto los gestiona el rol indicado por el protocolo;
QA no corrige el producto mientras evalúa la entrega.
