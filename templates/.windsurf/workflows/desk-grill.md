---
description: "Entrevista arquitectonica desktop mediante pausa estructurada en chat (A/B/C) para despejar frontera UF->UC, modulos MOD-*, FSM, persistencia local y contratos OS."
---

# /desk-grill — Entrevista Tecnica Desktop (Windsurf)

1. **"Codigo, Modulos y Esquemas primero, humano despues":**
   - Revisa `docs/functional/index.md`, `docs/design/tokens-and-themes.md`, `docs/technical/` y `graphify-out/` (si existe) antes de preguntar.
   - Prohibido preguntar hechos visibles en manifiestos, esquemas SQLite o documentacion.
2. **Pausa Estructurada en Chat:**
   - Presenta de **2 a 4 decisiones concretas** listando opciones claras con formato `A) (Recomendado) / B) / C)` y sus trade-offs.
   - Detente y espera la respuesta del usuario antes de redactar especificaciones o codigo.
3. **Aristas de Decision Desktop:**
   - **Frontera `UF-*` vs `UC-*` (`functional-boundary-guidelines.md`):** Escenario `full-module`, `domain-only` o `ui-only`, y reglas `[BR-XX]` / OCL.
   - **FSM, Concurrencia e Invariantes (`ui-contracts-guidelines.md`):** `NoDoubleSubmit`, `PreserveDraftOnError`, `NoMainThreadBlock` con cancelacion y `GuardUnsavedChangesOnClose`.
   - **Monolito Modular (`modular-architecture.md`):** Modulo dueno `MOD-*`, fachada publica y Event Bus en memoria.
   - **Ventanas, SO y Persistencia (`windowing-and-os-contracts.md`, `local-persistence.md`):** Topologia `WIN-*`, atajos `Ctrl` vs `Cmd`, accesibilidad OS, migraciones SQLite con backup previo, OS Keyring y Path Traversal.
   - **Brownfield Triage:** Verificar si un patron legado es *As-Is* o deuda para `docs/backlog/audit-proposals.md`.
4. **Cierre:**
   - Consolida los acuerdos y continua con `/desk-plan`.
