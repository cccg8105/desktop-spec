# Comando: 04_execute_requirement

> **Proposito:** Ejecutar la implementacion aprobada de un `REQ-DESK-*` dentro de sus fronteras autorizadas aplicando modularidad estricta, tokens nativos, contratos FSM y verificacion multi-nivel.

## Instrucciones para el Agente:
1. Lee unicamente el bloque `REQ-DESK-*` activo en `docs/backlog/pending.md` y sus documentos referenciados (`UF-*`, `UC-*`, `docs/design/`, `docs/technical/`).
2. **Descomposicion e Implementacion Acotada:**
   - Si el requerimiento abarca multiples capas, implementa en orden de dependencia interna: contratos/fachadas del modulo y reglas de dominio (`UC-*`) -> persistencia local y migraciones -> ViewModel/Presenter/FSM -> Vista/Ventana (`UF-*`).
   - Modifica **unicamente** los archivos listados en `Fronteras y Artefactos` (de lo contrario `dspec check --staged` bloqueara el commit).
   - Consume unicamente recursos/tokens definidos en `docs/design/tokens-and-themes.md` (soporte `light`, `dark`, `system`, `high-contrast` y densidad desktop), implementando invariantes UI (`NoDoubleSubmit`, `PreserveDraftOnError`, `FocusRestoration`, `NoMainThreadBlock`, `GuardUnsavedChangesOnClose`) y seguridad local (OS Keyring, Path Traversal, deserializacion segura).
3. **Verificacion Multi-Nivel:**
   - Ejecuta la suite de arquitectura modular + tests unitarios de dominio/BD + tests de ViewModel/UI Headless hasta obtener 100% de exito sin omisiones.
   - Si el requerimiento remedia vulnerabilidades o actualiza dependencias (`REQ-DESK-SEC-*`), valida el auditor local del ecosistema limpio y ejecuta `dspec check --security`.
   - Realiza auditoria del diff (`/code-review`) comprobando ausencia de acoplamiento entre internos de modulos, llamadas de persistencia desde vistas, colores/dimensiones quemadas o bloqueos del hilo UI.
4. **Cierre, Sync y Graphify:**
   - Marca `[x]` los criterios cumplidos en `docs/backlog/pending.md`, actualiza catálogos afectados (`dspec sync` y `dspec check`) manteniendo tablas *Rolling Window* con maximo 3 filas.
   - Si existe `graphify-out/`, ejecuta `graphify update` respetando `.graphifyignore`.
   - Cierra con `dspec resolve <REQ-DESK-ID>` (o `--bump` cuando complete el hito en `versioning-strategy.md`).
