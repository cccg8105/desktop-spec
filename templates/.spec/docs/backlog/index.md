# Indice del Backlog Desktop y Ciclo de Versiones — {{PROJECT_NAME}}

> **Instruccion para el Agente de IA:**
> Consulta este tablero antes de iniciar cualquier trabajo nuevo en el monolito modular desktop.
> - Busca en [`pending.md`](./pending.md) la tarea de mayor prioridad (`P1`) del milestone en curso.
> - Para cambios `MAJOR` o `MINOR`, verifica la frontera dual funcional (`UF-*` / `UC-*`) según `scope` y las referencias técnicas antes de editar código.
> - Para fixes `PATCH` (*Fast-Track*), sigue el protocolo `/diagnose` y verifica el test de regresión en [`pending.md`](./pending.md).
> - Nunca implementes deuda de [`audit-proposals.md`](./audit-proposals.md) directamente sin promoverla antes a [`pending.md`](./pending.md).

---

## Estado Operativo del Proyecto

- **Version Actual:** `v{{CURRENT_VERSION}}`
- **Milestone Activo:** `{{MILESTONE_VERSION}}`
- **Esquema de Versionamiento Activo:** `{{VERSIONING_SCHEME_LABEL}}` (ver [`versioning-strategy.md`](./versioning-strategy.md))

---

## Accesos Rapidos

| Documento | Descripcion |
| :--- | :--- |
| [pending.md](./pending.md) | **Requerimientos Pendientes:** Lista priorizada de tareas `REQ-DESK-*` delimitadas por módulos, artefactos y criterios de aceptación. |
| [audit-proposals.md](./audit-proposals.md) | **Auditoria y Mejoras (Solo Lectura):** Buzón de deuda técnica, fugas de frontera modular, *doc drift* y hallazgos Brownfield. |
| [changelog.md](./changelog.md) | **Historial de Releases:** Registro cronológico e inmutable de requerimientos resueltos por versión. |
| [versioning-strategy.md](./versioning-strategy.md) | **Gobernanza:** Protocolo de Dos Velocidades (`MAJOR`/`MINOR` vs. `PATCH` Fast-Track) y sincronización de manifiesto. |

---

## Resumen del Milestone Activo (`{{MILESTONE_VERSION}}`)

<!-- SYNC:BACKLOG_TABLE:START -->
_Sin requerimientos pendientes en el milestone actual._
<!-- SYNC:BACKLOG_TABLE:END -->
