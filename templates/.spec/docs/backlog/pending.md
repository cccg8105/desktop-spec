# Backlog de Requerimientos Pendientes — {{PROJECT_NAME}}

> **Instruccion para el Agente de IA:**
> Los requerimientos están organizados por milestones de versión y ordenados por prioridad (`P1` Alta, `P2` Media, `P3` Baja).
> 1. Modifica **unicamente** los módulos y archivos declarados en **Fronteras y Artefactos** (`[NEW]`, `[MODIFY]`, `[DELETE]`).
> 2. Respeta las restricciones de frontera (`UF-*` -> `UC-*` unidireccional, sin SQL en UI ni lógica UI en dominio) y verifica todos los criterios de aceptación (`[x]`) con `{{UNIT_TEST_RUNNER}}` y `{{UI_TEST_RUNNER}}`.
> 3. Para bugs o ajustes internos sin cambio de contrato (`PATCH`), utiliza el carril compacto *Fast-Track* con `N/A (PATCH / Fast-Track)` en `Flujos UX` y `Casos de Uso`.
> 4. Formato estricto de cada entrada (parseado por `desktop-spec check` / `dspec check`):

```markdown
### [REQ-DESK-DOMINIO-001] Titulo
- **Prioridad:** P1 | P2 | P3
- **Tipo:** Feature (MAJOR|MINOR) | Hotfix / Fix (PATCH - Fast-Track)
- **Alcance (Scope):** ui-only | domain-only | full-module | packaging-infra
- **Versión Objetivo:** `v...`
- **Flujos UX (`UF-*`):** `ruta` (o `N/A`)
- **Casos de Uso (`UC-*`):** `ruta` (o `N/A`)
- **Referencias Técnicas:** `ruta1`, `ruta2`
#### Fronteras y Artefactos:
- **Módulos Afectados:** `core`
- **Artefactos a Modificar / Crear:**
  - `ruta/archivo` [NEW|MODIFY|DELETE]
- **Restricciones:**
#### Criterios de Aceptación:
- [ ] ...
```

---

## Milestone {{MILESTONE_VERSION}}

*(Sin requerimientos pendientes. Ejecuta `desktop-spec req:new` o sigue el protocolo de planificación para registrar el primero).*
