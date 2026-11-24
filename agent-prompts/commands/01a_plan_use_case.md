# Comando: 01a_plan_use_case

> **Proposito:** Redactar o actualizar formalmente un caso de uso de dominio `UC-*` en Etapa 1 (Carril Completo `MAJOR` / `MINOR` para alcance `full-module` o `domain-only`).

## Instrucciones para el Agente:
1. Analiza las reglas de negocio, entradas/salidas DTO y persistencia local de forma estrictamente agnostica a ventanas, botones, atajos de teclado o toolkits UI (`.spec/templates/functional-boundary-guidelines.md`).
2. Identifica el modulo de dominio (`MOD-*`, ej. `core`, `catalog`, `billing`, `storage`) y asigna el siguiente ID secuencial (`UC-[MODULO]-[NUM]-[slug].md`).
3. Crea o actualiza `docs/functional/use-cases/UC-[MODULO]-[NUM]-[slug].md` tomando como molde `.spec/templates/_template_use_case.md`.
4. Incluye obligatoriamente:
   - Cabecera YAML Frontmatter (`id`, `title`, `module`, `actor`, `status`, `ocl_applied`, `trigger`).
   - Diagrama de proceso o secuencia de dominio en Mermaid (`flowchart TD` o `sequenceDiagram`).
   - Seccion `### Inputs Requeridos:` y `### Output Esperado:` en tablas estructuradas.
   - Reglas de negocio `- **[BR-01] ...:**` con contratos OCL (`pre`, `post` con `@pre`, `inv`) cuando aplique la Matriz Heuristica OCL (`.spec/templates/ocl-guidelines.md`).
   - Efectos secundarios locales (`local_database`, `local_files`, `os_keyring`, `internal_domain_events`) y excepciones tipadas de dominio (`[EX-XX]`).
   - Tabla `## Historial de Revisiones (Ultimos Cambios)` (maximo 3 filas).
5. Ejecuta `desktop-spec sync` (o `dspec sync`) y `dspec check` para actualizar `docs/functional/index.md` (`<!-- SYNC:USE_CASES_CATALOG:START/END -->`) y validar contra `schemas/use-case.schema.json`.
