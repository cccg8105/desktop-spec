# Indice de Documentacion Funcional — {{PROJECT_NAME}}

> **Instruccion para el Agente de IA:**
> Este catalogo centraliza los **Flujos de Interaccion (`UF-*`)** y los **Casos de Uso de Dominio (`UC-*`)** del monolito modular nativo.
> - Antes de planificar cambios funcionales o tecnicos, identifica aqui los artefactos afectados.
> - **No leas todos los archivos simultaneamente**; carga unicamente el `UF-*` o `UC-*` vinculado al requerimiento `REQ-DESK-*` en curso.
> - Respeta la frontera estricta unidireccional (`UF-*` delega en `UC-*` mediante `invokes_use_case`; `UC-*` nunca conoce ventanas ni UI) definida en [`functional-boundary-guidelines.md`](../../.spec/templates/functional-boundary-guidelines.md).
> - Plantillas canonicas: [`_template_user_flow.md`](../../.spec/templates/_template_user_flow.md), [`_template_use_case.md`](../../.spec/templates/_template_use_case.md), [`ui-contracts-guidelines.md`](../../.spec/templates/ui-contracts-guidelines.md) y [`ocl-guidelines.md`](../../.spec/templates/ocl-guidelines.md).

---

## Catalogo de Flujos de Interaccion (`UF-*`)

<!-- SYNC:USER_FLOWS_CATALOG:START -->
_Aun no hay flujos de interaccion registrados. Se agregaran automaticamente al formalizar requerimientos `MAJOR` o `MINOR` en `docs/functional/user-flows/`._
<!-- SYNC:USER_FLOWS_CATALOG:END -->

---

## Catalogo de Casos de Uso de Dominio (`UC-*`)

<!-- SYNC:USE_CASES_CATALOG:START -->
_Aun no hay casos de uso registrados. Se agregaran automaticamente al formalizar requerimientos `MAJOR` o `MINOR` en `docs/functional/use-cases/`._
<!-- SYNC:USE_CASES_CATALOG:END -->

---

## Modulos Legados Detectados (Modo Progresivo — Pendientes de Levantamiento As-Is)

<!-- SYNC:PENDING_MODULES:START -->
_Sin modulos legados pendientes de levantamiento._
<!-- SYNC:PENDING_MODULES:END -->

---

## Convenciones Funcionales del Monolito Modular

1. **Flujos de Interaccion (`UF-*`):** Residen en `docs/functional/user-flows/UF-[MODULO]-[NUMERO]-[slug].md` con YAML Frontmatter valido (`id`, `title`, `module`, `actor`, `window_target`, `entry_trigger`, `status`, `invokes_use_case`, `window_geometry`), diagrama Mermaid, matriz de estados UI, invariantes `ocl-ui` y accesibilidad nativa.
2. **Casos de Uso (`UC-*`):** Residen en `docs/functional/use-cases/UC-[MODULO]-[NUMERO]-[slug].md` con YAML Frontmatter valido (`id`, `title`, `module`, `actor`, `status`, `ocl_applied`, `trigger`), diagrama Mermaid de negocio, tablas de Inputs/Outputs, reglas `[BR-XX]` con OCL cuando aplica y efectos secundarios locales (`local_database`, `local_files`, `os_keyring`, `internal_domain_events`).
3. **Sincronizacion:** Ejecuta `desktop-spec sync` (o `dspec sync`) para mantener actualizados los bloques `SYNC` de este catalogo.
