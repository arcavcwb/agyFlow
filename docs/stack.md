# Stack de referencia y adaptación

El usuario indicó Plane, Astro, React, Next.js, Node.js, NestJS, Figma y Pencil
como contexto para esta plantilla. Este documento orienta la asignación de roles
y skills; las versiones, rutas, servicios y decisiones de cada aplicación se
definen en su `architecture.md` de gobernanza humana y sus manifests.

| Área | Referencia | Responsable |
|---|---|---|
| Requisitos | PRD e historias | PO |
| Planificación y estado | Plane | Scrum; operación manual o Automation asignado |
| Diseño | Figma y Pencil; tokens y componentes existentes | Designer |
| Interfaz | Astro, React y Next.js según superficie | Frontend |
| Servicios | Node.js y NestJS | Backend |
| Contratos compartidos | `packages/contracts` y Zod, convención de esta plantilla | Backend escribe; consumidores leen |
| Verificación | Navegador, API e integración según criterios | QA; autores realizan sus comprobaciones locales |
| Build y entrega | Herramientas y destino definidos por el proyecto | DevOps |

No se infiere qué aplicación usa cada framework ni una ruta para NestJS. La
arquitectura decide si Astro genera estáticos o requiere servidor, cómo se
integran componentes React, y cómo se ejecutan Next.js y los servicios Node.
Las configuraciones, convenciones de DTO y validación existentes deben leerse;
una skill externa no sustituye contratos Zod por otra librería automáticamente.

Para cada superficie visual, el proyecto elige el diseño de referencia y su
revisión. Si Figma y Pencil difieren, Designer resuelve cuál se implementa con
el humano antes de entregar; no se sincronizan dos versiones a ciegas.
La identidad de Pencil está pendiente de confirmar. La referencia a pencil.dev
del catálogo solo aplica si corresponde a la herramienta elegida.

Supabase y n8n venían referenciados en la plantilla inicial. Se mantienen como
opciones condicionadas a la arquitectura y a las tareas del proyecto. Tampoco
se impone un proveedor de hosting, contenedores o sistema de CI por instalar.

Usá `templates/project_setup.md` para registrar la adopción y las comprobaciones
por sesión sin duplicar las decisiones de arquitectura.
