# Comando: 01b_plan_user_flow

> **Proposito:** Redactar o actualizar formalmente un flujo de interaccion nativo `UF-*` en Etapa 1 (Carril Completo `MAJOR` / `MINOR` para alcance `full-module` o `ui-only`).

## Instrucciones para el Agente:
1. Analiza la interaccion del usuario con ventanas, dialogos, atajos y accesibilidad nativa respetando la frontera unidireccional hacia `UC-*` (`.spec/templates/functional-boundary-guidelines.md`). Prohibido incluir formulas de negocio, invariantes OCL de entidades o sentencias SQL en un `UF-*`.
2. Identifica el modulo funcional (`core`, `shell`, `catalog`, etc.) y asigna el siguiente ID secuencial (`UF-[MODULO]-[NUM]-[slug].md`).
3. Crea o actualiza `docs/functional/user-flows/UF-[MODULO]-[NUM]-[slug].md` tomando como molde `.spec/templates/_template_user_flow.md`.
4. Incluye obligatoriamente:
   - Cabecera YAML Frontmatter (`id`, `title`, `module`, `actor`, `window_target`, `entry_trigger`, `status`, `invokes_use_case`, `shortcut`, `fsm_required`, `window_geometry`).
   - Si el flujo ejecuta logica de negocio o persistencia, declara `invokes_use_case: UC-[MODULO]-[NUM]`; si es puramente presentacional (`ui-only`), declara `invokes_use_case: N/A`.
   - Diagrama Mermaid (`flowchart TD` o `stateDiagram-v2` cuando `fsm_required: true` segun `.spec/templates/ui-contracts-guidelines.md`).
   - Secciones `### Eventos / Entradas del Usuario:` y `### Salidas Visuales y Efectos:`.
   - `## 4. Matriz de Estados de Interfaz y Casos Borde` (`Idle`, `Loading`/`Busy`, `Empty`, `Error`, `Dirty`) e invariantes UI (`NoDoubleSubmit`, `PreserveDraftOnError`, `FocusRestoration`, `RollbackOnOptimisticFailure`, `NoMainThreadBlock`, `GuardUnsavedChangesOnClose`).
   - `## 6. Accesibilidad Nativa y Geometria` con `Foco Inicial y Teclado`, `Roles de Accesibilidad OS` (UI Automation / AT-SPI / NSAccessibility) y `Navegacion por Teclado` (`Ctrl` vs `Cmd`).
   - Tabla `## Historial de Revisiones (Ultimos Cambios)` (maximo 3 filas).
5. Ejecuta `desktop-spec sync` (o `dspec sync`) y `dspec check` para actualizar `docs/functional/index.md` (`<!-- SYNC:USER_FLOWS_CATALOG:START/END -->`) y validar contra `schemas/user-flow.schema.json`.
