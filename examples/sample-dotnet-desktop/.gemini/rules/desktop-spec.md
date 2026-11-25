---
trigger: always_on
description: "Reglas obligatorias de desktop-spec para Antigravity (Dos Velocidades, frontera UF->UC, monolito modular nativo, persistencia local, seguridad OS Keyring/Dependabot y Graphify)."
---

<!-- DESKTOP-SPEC:START -->
# Reglas Operativas — desktop-spec (Antigravity)

> Este bloque es gestionado por `desktop-spec`. No modifiques manualmente el contenido entre marcadores `DESKTOP-SPEC:START` y `DESKTOP-SPEC:END`.

## 1. Gatekeeper de Dos Velocidades
- **PROHIBIDO** editar codigo fuente (`src/`, `modules/`, `views/`, `ui/`, `tests/`) sin un `REQ-DESK-*` activo en `docs/backlog/pending.md` aprobado por el usuario.
- **Carril Completo (`MAJOR` / `MINOR`):** Flujo obligatorio `/grill-me` -> Frontera Funcional (`UF-*` con `_template_user_flow.md` + Matriz FSM `ui-contracts-guidelines.md` y/o `UC-*` con `_template_use_case.md` + OCL `ocl-guidelines.md`) -> Tokens (`tokens-and-themes.md`) / Arquitectura Modular (`MOD-*`) / Ventanas (`WIN-*`) y Persistencia Local / Empaquetado -> Test *Spec-First* (`_template_domain_test.md` / `_template_ui_test.md`) -> `docs/backlog/pending.md` -> `dspec sync && dspec check` -> Gatekeeper `/plan`.
- **Fast-Track (`PATCH`):** Solo bugs locales sin alterar contratos `UF-*`/`UC-*`, esquemas de persistencia ni fachadas `MOD-*`. Usa `Referencia Funcional: N/A (PATCH / Fast-Track)`, diagnostica con `/diagnose` + test de regresion en rojo, solicita confirmacion breve y aplica el fix minimo.

## 2. Monolito Modular Nativo, Frontera UF->UC y Contexto O(1)
- **Contexto Selectivo O(1):** Lee unicamente `docs/functional/index.md`, `docs/design/index.md`, `docs/technical/index.md` y los artefactos implicados antes de disenar. Si existe `graphify-out/graph.json`, consulta dependencias antes de leer archivos completos.
- **Entrevista (`/grill-me`):** Aplica *"Codigo, Modulos y Esquemas primero, humano despues"*. No preguntes datos observables en manifiestos, esquemas o documentacion.
- **Frontera Estricta `UF-*` vs `UC-*`:** `UF-*` describe ventanas, atajos, estados UI (`Idle`, `Busy`, `Empty`, `Error`, `Dirty`), accesibilidad nativa e invariantes (`NoDoubleSubmit`, `PreserveDraftOnError`, `FocusRestoration`, `NoMainThreadBlock`, `GuardUnsavedChangesOnClose`) y delega via `invokes_use_case`. `UC-*` gobierna DTOs, reglas `[BR-XX]` con OCL, SQLite/archivos y eventos internos sin mencionar controles visuales.
- **Fronteras Modulares:** Prohibido importar internos de otro modulo `MOD-*` o consultar persistencia directamente desde la UI. Todo modulo se consume via su fachada publica o Event Bus interno.
- **Tokens Simetricos:** Usa unicamente tokens de `docs/design/tokens-and-themes.md` (`light`, `dark`, `system`, `high-contrast` y densidad desktop). Prohibido quemar colores o metricas visuales.

## 3. Seguridad Local, Brownfield Just-In-Time y Cierre
- **Fronteras Estrictas:** Toca solo archivos declarados `[NEW]`, `[MODIFY]` o `[DELETE]` en `docs/backlog/pending.md`. Trata `docs/backlog/audit-proposals.md` (`[AUDIT-DESK-*]`) como solo lectura salvo promocion explicita a `REQ-DESK-*`.
- **Brownfield *Just-In-Time*:** Si el cambio afecta un modulo listado como `Pendiente As-Is` en `docs/functional/index.md`, documenta primero su comportamiento *As-Is* antes de planificar la evolucion *To-Be*. Para adopcion inicial usa `.gemini/skills/desktop-spec-bootstrap/SKILL.md`.
- **Seguridad Local y Dependabot (`gh` CLI):** Exige OS Keyring para secretos, canonizacion de rutas contra Path Traversal y deserializacion segura. Ante alertas de dependencias, verifica `gh auth status`, diagnostica con `gh api "repos/{owner}/{repo}/dependabot/alerts?state=open"` (`gh pr list --author "app/dependabot"` y auditor local `dotnet list package --vulnerable`, `pip-audit`, `cargo audit`, `gradle`). Tramita parches compatibles por **Fast-Track (`PATCH`)** bajo `REQ-DESK-SEC-*` y valida con `dspec check --security`; escala upgrades `MAJOR` con impacto en codigo fuente a `/plan`.
- **Verificacion, `/code-review` y Graphify:** Valida suite de arquitectura, dominio/SQLite y UI headless, ejecuta `/code-review` sobre el diff, manten maximo 3 filas en *Rolling Window* (`## Historial de Revisiones`) y ejecuta `graphify update` respetando `.graphifyignore`.
- **Empaquetado y Releases (`desktop-release`):** Para workflows multi-SO (`windows-latest`, `macos-latest`, `ubuntu-latest`), instaladores nativos, Code Signing & Notarization (`secrets.*` nunca en repo ni binario), canales `beta`/`stable` y Auto-Updater, activa `.gemini/skills/desktop-release/SKILL.md` (auditoria previa con `gh variable list` / `gh secret list`).
<!-- DESKTOP-SPEC:END -->
