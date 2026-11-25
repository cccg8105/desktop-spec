---
name: desktop-spec
description: "Orquestador completo del ciclo de vida desktop nativo Spec-Driven bajo Dos Velocidades (MAJOR/MINOR con frontera UF->UC, monolito modular y FSM vs PATCH Fast-Track) con soporte multi-ecosistema."
---

# desktop-spec Skill

Esta skill gobierna el ciclo completo de ingenieria para aplicaciones de escritorio **nativas** estructuradas como **monolito modular standalone** bajo **`desktop-spec`**, garantizando aislamiento entre modulos `MOD-*`, trazabilidad dual `UF-*` -> `UC-*`, seguridad local y verificacion multi-nivel.

## Regla de Oro (Gatekeeper de Dos Velocidades)
**PROHIBIDO** modificar codigo fuente (`src/`, `app/`, `modules/`, `views/`, `ui/`, `tests/`) sin un `REQ-DESK-*` activo en `docs/backlog/pending.md` aprobado por el usuario.

| Impacto (`versioning-strategy.md`) | Carril | Ceremonia Minima Exigida |
| :--- | :--- | :--- |
| **`MAJOR` / `MINOR`** (Nuevas features, ventanas `WIN-*`, modulos `MOD-*`, cambios de `UF-*`/`UC-*`, tokens o upgrade `MAJOR` que altere codigo) | **Carril Completo** | /grill-me -> Frontera Funcional (`UC-*` y/o `UF-*` + Matriz FSM) -> Tokens/Arquitectura Modular/Ventanas y Persistencia/Empaquetado -> Tests *Spec-First* (`_template_domain_test.md` / `_template_ui_test.md`) -> `pending.md` -> `dspec sync && dspec check` -> Gatekeeper `/plan`. |
| **`PATCH`** (Fix local sin cambiar contratos `UF-*`/`UC-*`, esquemas de BD ni fachadas `MOD-*`; o parche Dependabot compatible) | **Fast-Track** | `Referencia Funcional: N/A (PATCH / Fast-Track)`. Bloque compacto en `pending.md` (`REQ-DESK-SEC-*` si es seguridad) -> `/diagnose` (o `gh` + auditor local) + test de regresion en rojo -> confirmacion breve -> fix minimo. |

## Protocolo Operativo Estandar
1. **Contexto Selectivo O(1):** Consulta unicamente `docs/functional/index.md`, `docs/design/index.md` y `docs/technical/index.md` para cargar solo los artefactos implicados. Si existe `graphify-out/`, consulta acoplamientos antes de leer archivos completos.
2. **Aclaracion Preventiva (/grill-me):** Aplica la regla *"Codigo, Modulos y Esquemas primero, humano despues"*. Despeja ambiguedades antes de especificar (Pregunta de 2 a 4 decisiones por ronda en el chat colocando primero la opcion recomendada con trade-offs claros).
3. **Blueprints Obligatorios (`.spec/templates/`):**
   - Frontera Funcional: `functional-boundary-guidelines.md` (escenarios `full-module`, `domain-only` `uc-only`, `ui-only` `uf-only`).
   - Casos de Uso y OCL: `_template_use_case.md` y `ocl-guidelines.md` (sin referencias UI).
   - Flujos UX y FSM: `_template_user_flow.md` y `ui-contracts-guidelines.md` (sin SQL ni reglas de negocio).
   - Tokens y Diseno Nativo: `design-guidelines.md` y `_template_design_tokens.md` (`light`, `dark`, `system`, `high-contrast`, densidad desktop).
   - Pilares Tecnicos: `_template_modular_architecture.md`, `_template_windowing_os.md`, `_template_local_persistence.md`, `_template_tech_stack.md`, `_template_packaging_release.md`.
4. **Historial Rolling Window:** Manten maximo **3 filas** en `## Historial de Revisiones (Ultimos Cambios)` de cada documento.
5. **Fronteras Estrictas y Solo Lectura de Auditoria:** Toca exclusivamente archivos declarados `[NEW]`/`[MODIFY]`/`[DELETE]` en `docs/backlog/pending.md`. Trata `docs/backlog/audit-proposals.md` (`[AUDIT-DESK-*]`) como solo lectura salvo promocion explicita.
6. **Expansión Progresiva Brownfield:** Si el cambio toca un modulo en `Modulos Legados Detectados` dentro de `docs/functional/index.md`, documenta primero su comportamiento *As-Is* antes de planificar la evolucion *To-Be*.
7. **Seguridad Local, Dependabot (`gh`), `/code-review` y Cierre:**
   - Exige OS Keyring para credenciales, canonizacion contra Path Traversal y deserializacion segura.
   - Ante alertas de dependencias, verifica `gh auth status`, consulta `gh api "repos/{owner}/{repo}/dependabot/alerts?state=open"` y `gh pr list --author "app/dependabot"`, ejecuta el auditor local (`dotnet list package --vulnerable`, `pip-audit`, `cargo audit`, `gradle`) y valida con `desktop-spec check --security` (o `dspec check --security`), escalando upgrades `MAJOR` con impacto en codigo a `/plan`.
   - Ejecuta tests multi-nivel, realiza `/code-review` del diff, corre `dspec sync` y `dspec check`, actualiza `graphify update` respetando `.graphifyignore` y cierra con `dspec resolve <REQ-DESK-ID> [--bump]`.
