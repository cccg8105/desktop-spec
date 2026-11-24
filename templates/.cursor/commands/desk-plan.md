---
description: "Planifica un requerimiento desktop bajo desktop-spec (Dos Velocidades) usando AskQuestion antes de modificar codigo fuente."
---

# /desk-plan — Planificacion Spec-Driven Desktop (Cursor)

Objetivo: Planificar `$ARGUMENTS` aplicando el Gatekeeper de **Dos Velocidades** de `desktop-spec`. **PROHIBIDO editar codigo fuente** hasta que el usuario apruebe el requerimiento en `docs/backlog/pending.md`.

## Flujo de Trabajo

1. **Contexto Selectivo O(1):**
   - Consulta `docs/functional/index.md`, `docs/design/index.md`, `docs/technical/index.md` y `graphify-out/` (si existe) antes de inspeccionar multiples modulos.
   - Si el cambio toca modulos en `Modulos Legados Detectados`, documenta primero su comportamiento *As-Is* antes de disenar la evolucion *To-Be*.
2. **Evaluacion de Impacto (`MAJOR` / `MINOR` vs. `PATCH`):**
   - **Carril Completo (`MAJOR` / `MINOR`):** Despeja ambiguedades con `/desk-grill` (`AskQuestion`), formaliza `UC-*` y/o `UF-*`, Diagrama/Invariantes FSM (`ui-contracts-guidelines.md`), `tokens-and-themes.md`, `modular-architecture.md`, `windowing-and-os-contracts.md`, `local-persistence.md`, `tech-stack.md` / `packaging-and-release.md` y tests *Spec-First*.
   - **Fast-Track (`PATCH`):** Solo bugs locales o parches Dependabot compatibles (`REQ-DESK-SEC-*`, diagnosticados con `gh api "repos/{owner}/{repo}/dependabot/alerts?state=open"` y auditor local) sin cambiar contratos `UF-*`/`UC-*`, esquemas de BD ni fachadas `MOD-*`. Usa `Referencia Funcional: N/A (PATCH / Fast-Track)`, aplica `/diagnose` con test de regresion en rojo y prepara bloque compacto (upgrades `MAJOR` con impacto en codigo pasan a Carril Completo).
3. **Registro, Validacion y Espera de Aprobacion:**
   - Agrega el `REQ-DESK-*` en `docs/backlog/pending.md` declarando rutas `[NEW]`, `[MODIFY]`, `[DELETE]` y criterios de aceptacion.
   - Ejecuta `dspec sync` y `dspec check`.
   - Detente y solicita aprobacion explicita antes de implementar cambios en codigo fuente.
