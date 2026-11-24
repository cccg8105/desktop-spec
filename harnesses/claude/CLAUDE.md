<!-- DESKTOP-SPEC:START -->
# desktop-spec — Reglas Operativas para Claude Code

> Bloque gestionado por `desktop-spec`. No edites manualmente dentro de `DESKTOP-SPEC:START` / `DESKTOP-SPEC:END`.

## 1. Slash Commands Integrados
- **`/plan`**: Gatekeeper obligatorio antes de implementar cambios `MAJOR` o `MINOR`.
- **`/diff`**: Audita que los archivos modificados coincidan exactamente con las fronteras del `REQ-DESK-*`.
- **`/compact`**: Compacta contexto preservando el `REQ-DESK-*` activo y enlaces a `docs/`.
- **Comandos en `.claude/commands/`:**
  - `/desk-plan`: Flujo guiado de dos velocidades (`MAJOR`/`MINOR` completo vs `PATCH` Fast-Track).
  - `/desk-grill`: Entrevista arquitectonica interactiva (`AskUserQuestion`) sobre frontera `UF->UC`, modulos `MOD-*`, FSM, persistencia local y contratos OS.
  - `/desk-bootstrap`: Adopcion *Brownfield* en 4 fases con checklist persistente en `.spec/bootstrap-report.md`.
  - `/desk-resolve`: Cierre, verificacion y archivado seguro con `dspec resolve <REQ-DESK-ID> [--bump]`.

## 2. Protocolo Gatekeeper de Dos Velocidades
1. **PROHIBIDO codificar sin backlog:** Ningun archivo de codigo fuente puede modificarse sin un requerimiento `REQ-DESK-*` activo en `docs/backlog/pending.md` aprobado por el usuario.
2. **Carril Completo (`MAJOR` / `MINOR`):**
   - Despeja ambiguedades apoyandote en `/desk-grill`.
   - Si el requerimiento toca un modulo listado como `Pendiente As-Is` en `docs/functional/index.md`, documenta primero su comportamiento *As-Is* antes de disenar el cambio *To-Be*.
   - Aplica `.spec/templates/functional-boundary-guidelines.md`: documenta `UC-*` (`_template_use_case.md` + OCL) para dominio/persistencia y/o `UF-*` (`_template_user_flow.md` + Matriz FSM `ui-contracts-guidelines.md`) para ventanas e interaccion nativa, manteniendo delegacion unidireccional `UF -> invokes_use_case -> UC`.
   - Actualiza los documentos afectados en `docs/design/` (`tokens-and-themes.md` con modos `light`/`dark`/`system`/`high-contrast` y densidad) y `docs/technical/` (`modular-architecture.md`, `windowing-and-os-contracts.md`, `local-persistence.md`, `tech-stack.md`, `packaging-and-release.md`), respetando maximo 3 filas en `## Historial de Revisiones`.
   - Crea tests *Spec-First* (`_template_domain_test.md` / `_template_ui_test.md`), registra el `REQ-DESK-*` en `pending.md`, ejecuta `dspec sync` y `dspec check`, y espera aprobacion en `/plan`.
3. **Carril Fast-Track (`PATCH` / Hotfix sin cambio de contratos ni esquemas):**
   - Usa `Referencia Funcional: N/A (PATCH / Fast-Track)`.
   - Registra el `REQ-DESK-* (PATCH)` en `pending.md`, ejecuta `/diagnose` con test de regresion en rojo, solicita confirmacion breve y aplica el fix minimo.

## 3. Modularidad, Seguridad Local, Dependabot y Cierre
- **Monolito Modular y Solo Lectura:** Prohibido violar fronteras entre modulos `MOD-*` o acceder a persistencia desde vistas UI. Trata `docs/backlog/audit-proposals.md` (`[AUDIT-DESK-*]`) como solo lectura salvo promocion explicita a `pending.md`.
- **Seguridad Local:** Credenciales solo en OS Keyring (nunca en binario ni archivos planos), canonizacion de rutas contra Path Traversal y deserializacion segura.
- **Dependabot (`gh` CLI):** Ante vulnerabilidades en paquetes, verifica `gh auth status`, inspecciona `gh api "repos/{owner}/{repo}/dependabot/alerts?state=open"`, `gh pr list --author "app/dependabot"` y el auditor local (`dotnet list package --vulnerable`, `pip-audit`, `cargo audit`, `gradle`). Tramita parches compatibles por **Fast-Track (`PATCH`)** bajo `REQ-DESK-SEC-*` y valida con `dspec check --security`; escala upgrades `MAJOR` con impacto en codigo fuente a `/desk-plan`.
- **Revision, Tests y Graphify:** Ejecuta `/code-review` sobre el diff, corre tests de arquitectura + dominio/BD + UI headless, y si existe `graphify-out/`, ejecuta `graphify update` respetando `.graphifyignore`.
- **Empaquetado y Releases (`desktop-release`):** Para matriz CI multi-SO (`windows-latest`, `macos-latest`, `ubuntu-latest`), Code Signing & Notarization (`secrets.*` nunca en repo/binario), canales `beta`/`stable` y Auto-Updater, activa `.claude/skills/desktop-release/SKILL.md` (con `gh variable list` / `gh secret list`).
<!-- DESKTOP-SPEC:END -->
