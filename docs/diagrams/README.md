# Mapas visuales de agyFlow (Excalidraw / Excalidash)

Lienzos editables vectoriales compatibles con **Excalidash** y **Excalidraw**.

## 1. Diagrama Integral de los 6 Puntos Operativos
Cubre de forma exhaustiva las 6 dimensiones del framework agéntico:
- [Abrir archivo editable Excalidraw / Excalidash](agyflow-flujo-completo.excalidraw)
- [Vista previa vectorial SVG](agyflow-flujo-completo.svg)

| Marco | Contenido cubierto |
|---|---|
| **01 · Filosofía y Gobernanza Humana (HITL)** | Humano como Tech Lead, 3 Gates inviolables, Cero Asunción, IA como junior con permisos restringidos. |
| **02 · El Squad de 8 Agentes y Dominios** | Tarjetas con las 8 subagents, sus skills propias en `.agents/skills/`, dominios y reglas de oro. |
| **03 · Flujo de Entrega Handoff End-to-End** | Pipeline visual desde Brief, PRD, Plane, fases paralelas (Diseño/Contratos), Devs, QA y Staging/Prod. |
| **04 · Las Tres Reglas de Oro Operativas** | Pilares no negociables: 1. Cero Asunción, 2. Circuit Breaker (tope 3 rechazos con clave estable), 3. Un solo escritor. |
| **05 · Kit de Herramientas y Automatización CLI** | `validate_squad.py`, `handoff.py`, `setup_receiver.py`, suite local de tests unitarios y CI en GitHub Actions. |
| **06 · Cómo se Usa en la Práctica** | Guía paso a paso para inicializar y desarrollar un producto real en un proyecto receptor. |

---

## 2. Mapa Visual del SUPER MVP
Lienzo con cuatro zonas de análisis previo:
- [Abrir archivo editable](agyflow-super-mvp.excalidraw)
- [Vista previa vectorial SVG](agyflow-super-mvp.svg)
- [Vista previa en PNG](agyflow-super-mvp.png)

Los bordes continuos representan el protocolo documentado; no certifican que las
herramientas estén conectadas ni que las fases se hayan ejecutado. Los módulos
con borde discontinuo representan propuestas para discutir. La muestra de interfaz
es conceptual: no define marca, tokens reales ni una biblioteca ya implementada.
Las flechas rojas indican el retorno desde QA a corrección.

## Abrir en Excalidash

1. Descargar o localizar `agyflow-super-mvp.excalidraw` e iniciar sesión en la
   instancia propia de Excalidash.
2. Usar la importación de dibujos, si la versión instalada la ofrece, y seleccionar
   el archivo. El importador público consultado acepta escenas `.excalidraw`.
   [Código de importación de ExcaliDash](https://github.com/ZimengXiong/ExcaliDash/blob/main/frontend/src/utils/importUtils.ts).
3. Como alternativa, abrir un dibujo nuevo con el editor Excalidraw y usar su
   menú **Abrir / Open** para cargar el archivo local, si esa opción está habilitada
   por la instalación. No cargarlo sobre un dibujo que se quiera conservar.
4. Ajustar el zoom al contenido y acercar cada zona. Textos, tarjetas y flechas
   son elementos editables; cada zona tiene su propio marco.

La importación de un dibujo y la restauración de un respaldo `.excalidash` son
operaciones distintas; este archivo es una escena Excalidraw. El proyecto describe
su formato de respaldo por separado. [Repositorio de ExcaliDash](https://github.com/ZimengXiong/ExcaliDash#features).

La instancia facilitada por el usuario respondió y mostró inicio de sesión.
No se realizó una importación remota ni se comprobó el menú autenticado.
El archivo también puede abrirse en un editor Excalidraw independiente.

## Sesión de análisis recomendada

Elegir una historia esencial del producto y recorrer los cuatro mapas. Anotar
las decisiones en el lienzo y trasladar los acuerdos aprobados al PRD, arquitectura
humana o protocolo, según corresponda.

| Pilar | Decisión que conviene resolver | Evidencia propuesta |
|---|---|---|
| Visual | Qué pantalla y revisión fijan el nivel de calidad | Comparación visual del flujo principal y estados críticos |
| Seguridad | Qué personas pueden leer o modificar cada recurso sensible | Pruebas de acceso permitido y denegado, incluida la comprobación en servidor |
| Arquitectura | Dónde viven contratos y reglas de negocio | Rutas, responsables y consumidores identificados |
| Simplicidad | Qué piezas son necesarias para entregar el valor central | Motivo de las dependencias y reutilización de componentes existentes |

El lienzo sirve para analizar; las decisiones operativas siguen perteneciendo a
los documentos del proyecto. El sistema de diseño propuesto necesita adaptarse
a la marca, las superficies y los criterios reales antes de convertirse en requisito.

## Verificación y mantenimiento

Preparado el 12 de septiembre de 2026. Se verificaron referencias internas e IDs,
se cargaron los 316 elementos y cuatro marcos en un editor local Excalidraw 0.17.6
y se exportaron las vistas previas con su renderizador. Se revisaron visualmente
las cuatro zonas y no se detectaron líneas de texto que excedan el ancho asignado.
Esto comprueba la escena local; no acredita una importación autenticada al VPS.

El formato sigue la [estructura JSON oficial de Excalidraw](https://github.com/excalidraw/excalidraw/blob/master/dev-docs/docs/codebase/json-schema.mdx).
El archivo `.excalidraw` es el original editable. Tras modificarlo, volver a exportar
SVG y PNG para mantener las vistas previas alineadas y contrastar el contenido con
los documentos fuente si cambia el protocolo.
