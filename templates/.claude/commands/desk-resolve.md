---
description: "Implementa un requerimiento REQ-DESK-* aprobado de docs/backlog/pending.md respetando fronteras modulares, tokens nativos, FSM y verificacion."
---

# /desk-resolve — Ejecucion de Requerimiento Desktop Aprobado

Objetivo: Implementar el requerimiento `$ARGUMENTS` previamente aprobado en `docs/backlog/pending.md`.

## Guardias Previas a Codificar

1. Verifica que el `REQ-DESK-*` exista en `docs/backlog/pending.md`, este aprobado por el usuario y enumere explicitamente **Fronteras y Artefactos** (`[NEW]`, `[MODIFY]`, `[DELETE]`). Si no existe o faltan contratos (`UF-*`/`UC-*` para `MAJOR`/`MINOR`), detente y ejecuta `/desk-plan`.
2. **PROHIBIDO** modificar archivos fuera de las fronteras declaradas en el requerimiento o alterar `docs/backlog/audit-proposals.md`.

## Flujo de Implementacion y Verificacion

1. **Tests Spec-First en Rojo:** Crea o actualiza los tests de dominio/arquitectura/BD y/o ViewModel/UI Headless segun lo planificado y confirma su estado inicial antes de implementar.
2. **Implementacion Modular Nativa Estricta:**
   - Respeta fronteras entre modulos `MOD-*` (comunicacion unicamente via fachada publica o Event Bus interno; cero SQL en vistas).
   - Consume unicamente semantic design tokens de `docs/design/tokens-and-themes.md` (`light`, `dark`, `system`, `high-contrast` y densidad desktop).
   - Implementa la maquina de estados (FSM), trabajo asincrono sin bloquear UI (`NoMainThreadBlock`), `GuardUnsavedChangesOnClose`, restauracion de foco y seguridad local (OS Keyring, Path Traversal, deserializacion segura).
3. **Verificacion Multi-Nivel y `/code-review`:**
   - Ejecuta tests de arquitectura modular + dominio/persistencia local + ViewModel/UI headless hasta obtener 100% de exito.
   - Si se modificaron dependencias o alertas de Dependabot (`REQ-DESK-SEC-*`), valida el auditor local del ecosistema limpio y ejecuta `dspec check --security`.
   - Realiza auditoria del diff (`/code-review`) verificando ausencia de fugas entre modulos y cumplimiento de presupuestos desktop.
4. **Cierre Documental, Graphify y Resolve:**
   - Marca `[x]` los criterios de aceptacion en `docs/backlog/pending.md`, actualiza indices y tablas *Rolling Window* (maximo 3 filas), ejecuta `dspec sync` y `dspec check`, corre `graphify update` (si existe `graphify-out/`) y cierra con `dspec resolve <REQ-DESK-ID> [--bump]`.
