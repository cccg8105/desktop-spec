---
description: "Implementa un REQ-DESK-* aprobado en docs/backlog/pending.md respetando fronteras modulares, tokens nativos, FSM y tests de arquitectura/dominio/UI."
---

# /desk-execute — Implementacion de Requerimiento Desktop Aprobado (Windsurf)

1. **Validacion de Gatekeeper:**
   - Verifica que el `REQ-DESK-*` exista en `docs/backlog/pending.md`, este aprobado y declare **Fronteras y Artefactos** (`[NEW]`, `[MODIFY]`, `[DELETE]`). Si falta especificacion o aprobacion, detente y ejecuta `/desk-plan`.
   - Prohibido modificar archivos fuera de fronteras o editar `docs/backlog/audit-proposals.md`.
2. **Tests Spec-First en Rojo:**
   - Implementa o actualiza primero los tests de arquitectura modular/dominio/BD (`_template_domain_test.md`) y/o ViewModel/UI headless (`_template_ui_test.md`) definidos en la especificacion.
3. **Implementacion Modular Nativa Estricta:**
   - Respeta aislamiento entre modulos `MOD-*` (solo fachadas publicas y Event Bus interno; prohibido SQL en vistas).
   - Usa exclusivamente semantic design tokens de `docs/design/tokens-and-themes.md` (`light`, `dark`, `system`, `high-contrast` y densidad desktop).
   - Implementa FSM e invariantes (`NoDoubleSubmit`, `PreserveDraftOnError`, `FocusRestoration`, `NoMainThreadBlock`, `GuardUnsavedChangesOnClose`) y seguridad local (OS Keyring, Path Traversal, deserializacion segura).
4. **Verificacion, `/code-review` y Cierre:**
   - Ejecuta suite completa (arquitectura + dominio/SQLite + ViewModel/UI headless). Si el requerimiento cubre dependencias o Dependabot (`REQ-DESK-SEC-*`), valida auditor local y `dspec check --security`.
   - Ejecuta `/code-review` sobre el diff, marca `[x]` los criterios, ejecuta `dspec sync`, `dspec check`, actualiza tablas *Rolling Window* (maximo 3 filas), corre `graphify update` y cierra con `dspec resolve <REQ-DESK-ID> [--bump]`.
