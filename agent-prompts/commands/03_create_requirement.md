# Comando: 03_create_requirement

> **Proposito:** Sintetizar las especificaciones en un requerimiento atomico dentro de `docs/backlog/pending.md` con fronteras estrictas de archivos y pruebas iniciales, validado contra `schemas/requirement.schema.json`.

## Instrucciones para el Agente:
1. Consulta `docs/backlog/versioning-strategy.md` para clasificar el impacto, el alcance (`scope`) y el carril:
   - `MAJOR` / `MINOR` -> **Carril Completo** (exige `UF-*` y/o `UC-*` fisicos en disco segun `functional-boundary-guidelines.md`, y referencias tecnicas existentes).
   - `PATCH` -> **Carril Fast-Track** (permite `N/A (PATCH / Fast-Track)` si no cambia contratos funcionales, persistencia ni ventanas).
2. Asigna un ID unico `REQ-DESK-[DOMINIO]-[NUMERO]` verificando `docs/backlog/pending.md` y `docs/backlog/changelog.md` (o ejecuta `desktop-spec req:new` / `dspec req:new`).
3. Registra el bloque en `docs/backlog/pending.md` respetando el formato exacto:
   - `### [REQ-DESK-DOMINIO-NNN] Titulo`
   - `- **Prioridad:** P1 | P2 | P3`
   - `- **Tipo:** Feature (MINOR) | Breaking (MAJOR) | Hotfix / Fix (PATCH - Fast-Track)`
   - `- **Alcance (Scope):** ui-only | domain-only | full-module | packaging-infra`
   - `- **Version Objetivo:** \`v...\``
   - `- **Flujos UX (\`UF-*\`):** \`ruta\` (o \`N/A\`)`
   - `- **Casos de Uso (\`UC-*\`):** \`ruta\` (o \`N/A\`)`
   - `- **Referencias Tecnicas:** \`ruta1\`, \`ruta2\``
   - `#### Fronteras y Artefactos:` con `- **Modulos Afectados:**`, `- **Artefactos a Modificar / Crear:**` (`[NEW]`, `[MODIFY]`, `[DELETE]`) y `- **Restricciones:**`
   - `#### Criterios de Aceptacion:` con casillas `- [ ]` verificables mediante tests automatizados.
4. **Scaffolding Spec-First o Diagnostico `/diagnose`:**
   - En `MAJOR`/`MINOR`: crea los tests iniciales en rojo basados en `.spec/templates/_template_domain_test.md` (dominio/SQLite/arquitectura) y/o `.spec/templates/_template_ui_test.md` (ViewModel + UI Headless/Automation) con anotaciones `@spec`, `@req`, `@businessRule` / `@invariant`.
   - En `PATCH` (Fast-Track): aplica `/diagnose`:
     1. Reproduccion determinista del fallo.
     2. Aislamiento del caso minimo reproducible.
     3. Formulacion explicita de hipotesis de causa raiz.
     4. Test de regresion automatizado en rojo antes de editar la implementacion.
5. Ejecuta `dspec sync` y `dspec check` para validar enlaces, fronteras y esquemas.
6. **Gatekeeper:** Presenta el plan acotado (`/plan` o `/desk-plan` en Carril Completo, o resumen de diagnostico y test de regresion en `PATCH`) y **deten la ejecucion** hasta recibir aprobacion explicita del usuario.
