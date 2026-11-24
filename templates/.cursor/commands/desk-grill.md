---
description: "Entrevista tecnica desktop (frontera UF->UC, modulos MOD-*, FSM, concurrencia, persistencia local y contratos OS) mediante tarjetas interactivas AskQuestion."
---

# /desk-grill — Entrevista Arquitectonica Desktop (Cursor)

Objetivo: Resolver decisiones abiertas funcionales, modulares, de persistencia y de UI nativa para `$ARGUMENTS` antes de redactar especificaciones o codigo.

## Reglas del Entrevistador

1. **"Codigo, Modulos y Esquemas primero, humano despues":**
   - Inspecciona `docs/functional/index.md`, `docs/design/tokens-and-themes.md`, `docs/technical/` y `graphify-out/` (si existe) antes de preguntar.
   - No preguntes datos observables en manifiestos, esquemas locales, codigo fuente o documentacion existente.
2. **Entrevista por Tarjeta Interactiva (`AskQuestion`):**
   - Presenta de **2 a 4 decisiones concretas** usando `AskQuestion`, ubicando primero la opcion `(Recommended)` con su justificacion y trade-offs.
3. **Areas Clave Desktop:**
   - **Frontera `UF-*` vs `UC-*` (`functional-boundary-guidelines.md`):** Escenario `full-module`, `domain-only` o `ui-only`, mas reglas `[BR-XX]` / OCL.
   - **FSM, Concurrencia e Invariantes (`ui-contracts-guidelines.md`):** `NoDoubleSubmit`, `PreserveDraftOnError`, `NoMainThreadBlock` con cancelacion y `GuardUnsavedChangesOnClose`.
   - **Monolito Modular (`modular-architecture.md`):** Modulo dueno `MOD-*`, fachada publica y eventos internos.
   - **Ventanas, SO y Persistencia (`windowing-and-os-contracts.md`, `local-persistence.md`):** Topologia `WIN-*`, atajos `Ctrl` vs `Cmd`, accesibilidad OS, migraciones SQLite con respaldo previo, OS Keyring y Path Traversal.
   - **Brownfield Triage:** Confirma si un comportamiento heredado es *As-Is* intencional o deuda para `docs/backlog/audit-proposals.md`.
4. **Cierre:**
   - Resume los acuerdos alcanzados y formaliza los artefactos afectados o continua con `/desk-plan`.
