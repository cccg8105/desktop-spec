---
description: "Planifica un requerimiento desktop siguiendo desktop-spec (Dos Velocidades) y deteniendose para aprobacion antes de implementar."
---

# /desk-plan — Planificacion Spec-Driven Desktop (Windsurf)

1. **Contexto Selectivo O(1):**
   - Lee `docs/functional/index.md`, `docs/design/index.md` y `docs/technical/index.md` (y consulta `graphify-out/graph.json` si existe) antes de explorar multiples archivos fuente.
   - Si toca modulos en `Modulos Legados Detectados`, documenta primero su comportamiento *As-Is*.
2. **Clasificacion de Impacto (`docs/backlog/versioning-strategy.md`):**
   - **`MAJOR` / `MINOR` (Carril Completo):** Ejecuta `/desk-grill` si hay decisiones abiertas sobre frontera `UF->UC`, modulos `MOD-*`, FSM, concurrencia, persistencia o contratos OS. Luego redacta o actualiza `UC-*` y/o `UF-*`, tokens, pilares tecnicos afectados y los tests *Spec-First*.
   - **`PATCH` (Fast-Track):** Para bugs locales o parches Dependabot compatibles (`REQ-DESK-SEC-*` verificados via `gh api "repos/{owner}/{repo}/dependabot/alerts?state=open"` y auditor local) sin cambiar contratos `UF-*`/`UC-*`, esquemas de BD ni fachadas `MOD-*`. Usa `Referencia Funcional: N/A (PATCH / Fast-Track)`, aplica `/diagnose` y prepara test de regresion en rojo (upgrades `MAJOR` con impacto en codigo pasan a Carril Completo).
3. **Registro y Validacion en `docs/backlog/pending.md`:**
   - Crea la entrada `REQ-DESK-*` declarando rutas exactas (`[NEW]`, `[MODIFY]`, `[DELETE]`) y criterios de aceptacion.
   - Ejecuta `dspec sync` y `dspec check`.
4. **Gatekeeper Obligatorio:**
   - Detente sin modificar codigo fuente y presenta el resumen al usuario. Una vez aprobado, ejecuta `/desk-execute`.
