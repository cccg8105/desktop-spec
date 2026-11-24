---
description: "Entrevista tecnica desktop previa (frontera UF->UC, modulos MOD-*, FSM, concurrencia, persistencia local y contratos OS) mediante AskUserQuestion."
---

# /desk-grill — Entrevista Arquitectonica Desktop

Objetivo: Despejar todas las ambiguedades funcionales, modulares, de persistencia y de experiencia nativa para `$ARGUMENTS` antes de especificar o codificar.

## Reglas de Entrevista

1. **"Codigo, Modulos y Esquemas primero, humano despues":**
   - Inspecciona `docs/functional/index.md`, `docs/design/tokens-and-themes.md`, `docs/technical/` y `graphify-out/` (si existe) antes de formular cualquier pregunta.
   - Prohibido preguntar datos que ya constan en manifiestos, esquemas SQLite, vistas XAML/QML/Compose o documentacion.
2. **Rondas Quirurgicas con `AskUserQuestion`:**
   - Formula entre **2 y 4 decisiones concretas** por ronda mediante `AskUserQuestion`, colocando siempre la opcion recomendada primero con el prefijo `(Recommended)` y explicando los trade-offs.
3. **Ejes del Arbol de Decision Desktop:**
   - **Frontera Funcional (`functional-boundary-guidelines.md`):** Escenario `full-module` (`UF -> UC`), `domain-only` (`uc-only`) o `ui-only` (`uf-only`), mas reglas `[BR-XX]` / OCL.
   - **FSM, Concurrencia e Invariantes (`ui-contracts-guidelines.md`):** Proteccion contra doble envio (`NoDoubleSubmit`), borrador ante error (`PreserveDraftOnError`), trabajo en background sin bloquear UI (`NoMainThreadBlock` + cancelacion) y guardia al cerrar (`GuardUnsavedChangesOnClose`).
   - **Arquitectura Modular (`modular-architecture.md`):** Modulo dueno `MOD-*`, fachada publica y eventos en Event Bus interno.
   - **Ventanas, SO y Persistencia (`windowing-and-os-contracts.md`, `local-persistence.md`):** Topologia de ventana `WIN-*`, atajos `Ctrl` vs `Cmd`, accesibilidad OS, migraciones SQLite con respaldo previo y seguridad local (OS Keyring, Path Traversal).
   - **Brownfield Triage:** Pregunta si un acoplamiento o comportamiento legado detectado es *As-Is* intencional o deuda para `docs/backlog/audit-proposals.md`.
4. **Cierre:**
   - Resume los acuerdos alcanzados y procede a formalizarlos o a ejecutar `/desk-plan`.
