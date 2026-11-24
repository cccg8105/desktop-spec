---
description: "Planifica un requerimiento desktop (Carril Completo MAJOR/MINOR o Fast-Track PATCH) usando desktop-spec sin tocar codigo fuente antes de aprobacion."
---

# /desk-plan — Planificacion Spec-Driven Desktop

Objetivo: Planificar `$ARGUMENTS` siguiendo el protocolo de **Dos Velocidades** de `desktop-spec`. **NO edites codigo fuente** hasta recibir aprobacion explicita del usuario sobre el `REQ-DESK-*` en `docs/backlog/pending.md`.

## Pasos Obligatorios

1. **Contexto Selectivo O(1):**
   - Lee `docs/functional/index.md`, `docs/design/index.md` y `docs/technical/index.md`.
   - Si existe `graphify-out/graph.json`, consulta los nodos relacionados antes de abrir archivos fuente.
   - Si el cambio afecta un modulo en `Modulos Legados Detectados`, documenta primero su comportamiento *As-Is* antes de disenar el cambio *To-Be*.
2. **Clasificacion de Impacto (`docs/backlog/versioning-strategy.md`):**
   - **`MAJOR` / `MINOR` (Carril Completo):** Ejecuta primero `/desk-grill` si existen decisiones abiertas sobre frontera `UF->UC`, modulos `MOD-*`, FSM, concurrencia, persistencia local o contratos OS (usa `AskUserQuestion` con `(Recommended)` primero). Luego formaliza `UC-*` y/o `UF-*`, tokens, pilares tecnicos afectados (`modular-architecture.md`, `windowing-and-os-contracts.md`, `local-persistence.md`, `tech-stack.md`, `packaging-and-release.md`) y el blueprint de test *Spec-First* (`_template_domain_test.md` / `_template_ui_test.md`).
   - **`PATCH` (Fast-Track):** Ajustes internos locales o remediaciones Dependabot compatibles (`REQ-DESK-SEC-*` diagnosticados con `gh api "repos/{owner}/{repo}/dependabot/alerts?state=open"` + auditor local) sin cambiar contratos `UF-*`/`UC-*`, esquemas de BD ni fachadas `MOD-*`. Usa `Referencia Funcional: N/A (PATCH / Fast-Track)`, aplica `/diagnose` con test de regresion en rojo y prepara bloque compacto en `docs/backlog/pending.md` (escala upgrades `MAJOR` con impacto en codigo fuente a Carril Completo).
3. **Gatekeeper de Fronteras:**
   - Registra el requerimiento `REQ-DESK-*` en `docs/backlog/pending.md` con rutas exactas `[NEW]`, `[MODIFY]` y `[DELETE]` y criterios de aceptacion verificables.
   - Ejecuta `dspec sync` y `dspec check`.
   - Detente y presenta el plan al usuario para su aprobacion explicita antes de pasar a `/desk-resolve`.
