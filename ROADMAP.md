# Roadmap de Construcción y Plan `/teamwork` — desktop-spec

Este plan divide la construcción completa de `desktop-spec` en **fases iterativas e incrementales** (de `v0.1.0` hasta `v1.0.0` y extensión `v1.1+`) y define los **carriles independientes** preparados para ejecutarse en paralelo con múltiples agentes mediante `/teamwork` sin colisiones de archivos.

---

## 1. Plan Estructurado por Fases (Iterativo e Incremental)

### Fase 0 — Estructura del Repositorio y Contratos Conceptuales *(Completada)*
- **Objetivo:** Establecer la anatomía del repositorio, la definición de los 5 componentes principales, el alcance *native-first* sin backend propio y la frontera estricta `UC-*` vs. `UF-*`.
- **Entregables:** `README.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `CHANGELOG.md`, `pyproject.toml`, `.gitignore` y árbol de directorios esqueleto.
- **Criterio de Salida:** Árbol de directorios creado y arquitectura revisada sin ambigüedades entre `UC-*` y `UF-*`.

### Fase 1 — Contratos Formales y Normativa Base (`v0.2.0-dev`) *(Completada en Wave 1)*
- **Objetivo:** Congelar el esquema de datos, metadatos YAML Frontmatter y reglas normativas antes de escribir plantillas o código del CLI.
- **Entregables:**
  - `schemas/requirement.schema.json` (soportando `REQ-DESK-*`, `scope`, `references.user_flows`, `references.use_cases`, `references.technical` y `boundaries.affected_modules`).
  - `schemas/use-case.schema.json` y `schemas/user-flow.schema.json` (con campo `invokes_use_case` y prohibición cruzada documentada).
  - `schemas/design/tokens-and-themes.schema.json` (modos `light`, `dark`, `system`, `high-contrast`, escala de densidad desktop).
  - 5 esquemas técnicos en `schemas/technical/`: `tech-stack.schema.json`, `modular-architecture.schema.json`, `windowing-and-os-contracts.schema.json`, `local-persistence.schema.json`, `packaging-and-release.schema.json`.
  - Plantilla base `templates/.spec/config.yaml` (perfil de ecosistema desktop nativo, `version_file` y `modules`).
  - Guías normativas en `templates/.spec/templates/`: `ocl-guidelines.md`, `ui-contracts-guidelines.md` (con invariantes `NoMainThreadBlock` y `GuardUnsavedChangesOnClose`), `design-guidelines.md` y `functional-boundary-guidelines.md`.
- **Criterio de Salida:** Todos los JSON Schemas validados sintácticamente dentro del subconjunto Draft-07 sin dependencias y auditados por `w1-contract-auditor`.

### Fase 2 — Activos del Agente: Blueprints, Prompts, Skills y Harnesses (`v0.3.0-dev`) *(Completada en Wave 2)*
- **Objetivo:** Completar todo el contenido textual y parametrizado que `init` y `update` distribuirán hacia proyectos consumidores.
- **Entregables:**
  - Documentos base limpios en `templates/.spec/docs/` (`functional/`, `design/`, `technical/`, `backlog/`).
  - Blueprints en `templates/.spec/templates/` (`_template_use_case.md`, `_template_user_flow.md`, `_template_design_tokens.md`, `_template_tech_stack.md`, `_template_modular_architecture.md`, `_template_windowing_os.md`, `_template_local_persistence.md`, `_template_packaging_release.md`, `_template_domain_test.md`, `_template_ui_test.md`, `_template_audit_proposals.md`).
  - Protocolo agnóstico en `agent-prompts/AGENTS.md` y comandos `01` a `04` (separando planificación funcional dual, arquitectura modular, persistencia local, windowing/OS y packaging).
  - 5 skills en `templates/.spec/skills/`: `desktop-spec`, `desktop-spec-bootstrap`, `desk-grill`, `desktop-testing`, `desktop-release`.
  - Adaptadores multi-harness en `harnesses/` (`antigravity`, `claude`, `cursor`, `windsurf`), comandos `/desk-*` en `templates/.{claude,cursor,windsurf}/`, `templates/.githooks/pre-commit`, `templates/.github/workflows/desktop-spec-check.yml`, `templates/.gitignore` y `templates/.graphifyignore`.
- **Criterio de Salida:** Todos los placeholders (`{{PROJECT_NAME}}`, `{{ECOSYSTEM_NAME}}`, `{{CURRENT_VERSION}}`, `{{HARNESS_INTERVIEW_TRIGGER}}`, etc.) consistentes y cero enlaces rotos internos en `templates/`.

### Fase 3 — Motor CLI Determinista en Python Stdlib (`v0.4.0-dev`) *(Completada en Waves 2 y 3)*
- **Objetivo:** Implementar el CLI ejecutable `desktop-spec` (`dspec`) y su suite de pruebas automatizadas sin dependencias externas.
- **Entregables:**
  - *(Completado en Wave 2)* `cli/desktop_spec/common.py`, `cli/desktop_spec/detector/ecosystem_detector.py` (11 perfiles nativos y detección `empty`/`scaffold`/`brownfield`), `cli/desktop_spec/detector/version_extractor.py` (`xml`, `toml`, `gradle`, `cfg`, `cmake`, `plain`, `json`), `cli/desktop_spec/validator/schema_validator.py` (YAML Frontmatter, Draft-07 `stdlib` con `type` string/lista, extractores `UC-*`/`UF-*`/`REQ-DESK-*`/`tokens` y exportación/validación W3C DTCG) y sus pruebas unitarias (`test_ecosystem_detector.py`, `test_version_extractor.py`, `test_validator_and_negative.py`).
  - *(Completado en Wave 3)* `cli/main.py`, `cli/desktop_spec/__main__.py`, wrappers `dspec` / `dspec.ps1`, los 7 subcomandos en `cli/desktop_spec/commands/` (`init_cmd.py`, `update_cmd.py`, `bootstrap_cmd.py`, `new_req_cmd.py`, `sync_index_cmd.py`, `check_cmd.py`, `resolve_cmd.py`) y pruebas de integración (`test_update_and_brownfield.py`, `test_cli_workflow.py`).
- **Criterio de Salida:** `python -m unittest discover -s cli/tests -v` pasando al 100% (41/41 pruebas) en Windows y Linux.

### Fase 4 — Proyectos Piloto, Guías Hub & Spoke y Automatización de Release (`v1.0.0`) *(Completada en Wave 4)*
- **Objetivo:** Validar el framework de extremo a extremo sobre proyectos nativos reales de referencia, publicar guías operativas y congelar contratos públicos `v1.0.0`.
- **Entregables:**
  - Proyecto piloto 1 en `examples/` (ej. `.NET Avalonia` o `WPF` monolito modular con SQLite local, `UC-*` + `UF-*`, validado sin advertencias con `dspec check`).
  - Proyecto piloto 2 en `examples/` (ej. `Python PySide6` o `Kotlin Compose Desktop`, validado con `dspec check`).
  - 4 guías modulares en `guides/` (`01-new-projects-greenfield.md`, `02-existing-projects-brownfield.md`, `03-daily-workflow-two-speeds.md`, `04-cli-harnesses-and-contracts.md`) + `README.md` ejecutivo actualizado.
  - Automatización del repositorio: ampliación de `scripts/bump_version.py` (ya activo desde `v0.1.0` para archivos base) cubriendo los artefactos de Waves 2 y 3 (`agent-prompts/AGENTS.md`, `templates/.githooks/pre-commit`, `templates/.spec/docs/backlog/changelog.md`), más `.github/workflows/ci.yml` y `.github/workflows/release.yml` verificando build `wheel`/`sdist` con Hatchling.
- **Criterio de Salida:** Ambos pilotos validan ciclo `init -> bootstrap -> req:new -> sync -> check -> resolve` y CI en verde para etiquetar `v1.0.0`.

### Fase 5 — Extensión Posterior (`v1.1.0+`) *(Completada en Wave 5)*
- **Objetivo:** Incorporar perfiles adicionales sin romper compatibilidad `v1.0.0`:
  - Shells híbridos con WebView (`tauri`, `electron`, `wails`) añadiendo soporte de contratos IPC/FFI y sincronización multi-manifiesto en `version_extractor.py`.
  - Perfiles nativos adicionales (`flutter-desktop`, `swift-macos`).

### Fase 6 — Alineación Documental y Consistencia Pre-Release *(Pendiente en Wave 6)*
- **Objetivo:** Eliminar el *doc drift* interno entre las guías operativas, `README.md`, `AGENTS.md`, skills y el comportamiento real del CLI y sus 16 ecosistemas antes de etiquetar una versión estable.
- **Entregables:**
  - Corrección integral de `guides/01..04`: sintaxis real de `dspec req:new` (`--impact`, `--scope`, `--from-audit AUDIT-DESK-*`), rutas reales (`modular-architecture.md`, `tokens-and-themes.md`, `docs/functional/user-flows/`), definición exacta de Rolling Window (`<= 3` filas en `## Historial de Revisiones`), rol de `.spec/bootstrap-report.md`, `--security`, `maui-desktop`, `.windsurfrules` y catálogo real de los 9 esquemas Draft-07.
  - Propagación de los 16 ecosistemas y 4 proyectos piloto en `README.md`, `guides/04`, `agent-prompts/AGENTS.md`, `templates/.spec/config.yaml` (comentarios de perfiles/formatos) y `templates/.spec/skills/`.
  - Actualización de `cli/tests/test_packaging_and_e2e.py` usando `desktop_spec.__version__` dinámico, cubriendo los 4 pilotos en `examples/` y añadiendo pruebas automatizadas contra *doc drift* en `guides/`.
- **Criterio de Salida:** Cero desalineaciones entre `guides/` y `dspec --help`, 4/4 pilotos verificados en `test_packaging_and_e2e.py`, `bump_version.py --check` y `unittest` al 100%.

### Fase 7 — Endurecimiento del Motor CLI y Paridad Multi-Ecosistema *(Pendiente en Wave 7)*
- **Objetivo:** Cerrar brechas funcionales en `check`, `resolve` y `bootstrap` para garantizar paridad determinista en los 16 ecosistemas.
- **Entregables:**
  - `check_cmd.py`: eliminar bypass en `--staged` cuando `docs/` también está en stage, cubrir archivos fuente en raíz (`Program.cs`, `main.py`, `app.go`), ampliar `--strict-tokens` a extensiones y raíces de Wave 5 (`.tsx`, `.jsx`, `.ts`, `.css`, `.dart`, `.swift`, `lib/`, `Sources/`, `frontend/src/`), y completar la validación de `density_modes`/`typography`/`window_chrome` más secciones clave de los 5 pilares técnicos Markdown.
  - `resolve_cmd.py`: invocar `sync_multi_manifest_versions()` en `--bump` para híbridos multi-manifiesto y sincronizar `## Milestone` en `pending.md` junto con `docs/backlog/index.md`.
  - `bootstrap_cmd.py`: extender el inventario Brownfield y el detector de *doc drift* a Tauri, Electron, Wails, Flutter Desktop y Swift macOS.
- **Criterio de Salida:** Suite de regresión específica por cada corrección y 100% de tests `unittest` en verde sobre los 16 perfiles.

### Fase 8 — Experiencia Greenfield (Día 0) y Adopción Progresiva Brownfield *(Pendiente en Wave 8)*
- **Objetivo:** Eliminar fricciones en el arranque de proyectos nuevos y facilitar la adopción incremental en repositorios legados reales.
- **Entregables:**
  - **Greenfield:** soporte explícito para el commit fundacional del scaffold sin choque con `pre-commit`, corrección de `update --refresh-stack` para evitar residuos del perfil por defecto (`avalonia`) al partir de un directorio `empty`, y flag opcional `dspec req:new --scaffold-specs` para generar borradores `UF-*.md` / `UC-*.md` desde `.spec/templates/`.
  - **Brownfield:** detección de monolitos legados planos sin carpeta `modules/` (evitando que el fallback `core` oculte módulos pendientes en `docs/functional/index.md`), convivencia y análisis de *doc drift* ante carpetas `docs/` preexistentes, y modo de transición gradual (`check --warn-only` / baseline temporal).
- **Criterio de Salida:** Tests E2E completos simulando un repo vacío (`git init -> dspec init -> scaffold -> refresh-stack -> primer commit`) y un repo legado plano con `docs/` previos.

### Fase 9 — Guardrails Avanzados y Escalabilidad en Equipo *(Pendiente en Wave 9)*
- **Objetivo:** Reforzar la verificación automática offline de seguridad y fronteras modulares, y reducir conflictos de merge en trabajo paralelo multi-rama.
- **Entregables:**
  - **Seguridad local offline:** complementar `check --security` (Dependabot/`gh`) con escáner local liviano de secretos hardcodeados e integración opcional con auditores nativos locales (`dotnet list package --vulnerable`, `pip-audit`, `cargo audit`, `npm audit`).
  - **Fronteras verificables (`--check-boundaries`):** heurísticas deterministas anti-contaminación en `UF-*.md` / `UC-*.md`, chequeo estático ligero de imports cruzados indebidos en `modules_dir`, y blueprints de tests de arquitectura por ecosistema (`NetArchTest`, `import-linter`, `ArchUnit`).
  - **Backlog concurrente anti-colisión:** soporte aditivo de requerimientos por archivo individual (`docs/backlog/items/REQ-DESK-*.md`) agregados por `dspec sync`, manteniendo 100% retrocompatibilidad con `pending.md`.
- **Criterio de Salida:** Pruebas positivas/negativas para fugas de frontera, secretos locales y backlog multi-archivo sin romper retrocompatibilidad `v1.0.0`.

---

## 2. Estrategia de Paralelismo Multi-Agente (`/teamwork`)

Para aprovechar `/teamwork` de forma efectiva sin conflictos de edición sobre los mismos archivos ni contradicciones entre agentes, el trabajo se organiza en **9 Oleadas (*Waves*)** con **propiedad de rutas estrictamente disjunta**.

### Regla de Coordinación en `/teamwork`
1. **Ciclo Git Automático por Oleada (`.gemini/rules/repo-workflow.md`):** Antes de lanzar los workers de una oleada, el **Coordinador** sincroniza `main` y crea automáticamente la rama de trabajo (`feat/wave-N-...`). Al cerrar el gate final de la oleada en verde, actualiza `ROADMAP.md` + `CHANGELOG.md` y realiza automáticamente el `git commit` local en esa rama (sin `git push` hasta que el usuario lo solicite).
2. **Ningún par de workers comparte escritura sobre el mismo directorio o archivo en una misma oleada.**
3. **Wave 1 congela el contrato** (`schemas/`, `config.yaml`, convenciones de placeholders y Frontmatter). Ningún worker posterior inventa nombres de campos por su cuenta: lee directamente `schemas/`.
4. El agente **Coordinador** planifica detenidamente (`/plan`) cada oleada antes de lanzarla y verifica integridad entre oleadas.

### Mapa de Oleadas y Carriles Paralelos

| Oleada | Fase(s) del Plan | Carriles en Paralelo (`/teamwork`) | Propiedad Exclusiva de Archivos | Dependencia de Entrada | Gate de Cierre |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Wave 1** *(Contratos Raíz — Completada)* | **Fase 1** *(completa)* | **W1-A (Fase 1 — Funcional y Diseño)**<br>**W1-B (Fase 1 — Técnico y Gobernanza)**<br>**W1-Audit (Gate solo lectura)** | **W1-A:** `schemas/use-case.schema.json`, `schemas/user-flow.schema.json`, `schemas/design/*`, `templates/.spec/templates/{ocl,ui-contracts,design,functional-boundary}-guidelines.md`<br>**W1-B:** `schemas/requirement.schema.json`, `schemas/technical/*`, `templates/.spec/config.yaml` | `ARCHITECTURE.md` (Fase 0) | Revisión cruzada de claves Frontmatter, prefijos (`REQ-DESK-*`, `UC-*`, `UF-*`) y validez JSON Draft-07 (`[audit-ok]`). |
| **Wave 2** *(Activos + Core CLI — Completada)* | **Fase 2** *(completa)* + **Fase 3** *(parte 1: Detectores y Validador)* | **W2-A (Fase 2 — Templates Funcionales/Diseño)**<br>**W2-B (Fase 2 — Templates Técnicos/Backlog)**<br>**W2-C (Fase 2 — Prompts, Skills y Harnesses)**<br>**W2-D (Fase 3 — Detectores y Versiones)**<br>**W2-E (Fase 3 — Validador Draft-07)**<br>**W2-Audit (Gate solo lectura)** | **W2-A:** `templates/.spec/docs/{functional,design}/`, `templates/.spec/templates/_template_{use_case,user_flow,design_tokens,domain_test,ui_test}.md`<br>**W2-B:** `templates/.spec/docs/{technical,backlog}/`, `templates/.spec/templates/_template_{tech_stack,modular_architecture,windowing_os,local_persistence,packaging_release,audit_proposals}.md`<br>**W2-C:** `agent-prompts/`, `harnesses/`, `templates/.{claude,cursor,windsurf,githooks,github}/`, `templates/.spec/skills/`, `templates/.{gitignore,graphifyignore}`<br>**W2-D:** `cli/desktop_spec/detector/`, `cli/tests/test_{ecosystem_detector,version_extractor}.py`<br>**W2-E:** `cli/desktop_spec/validator/`, `cli/desktop_spec/common.py`, `cli/tests/test_validator_and_negative.py` | Contratos congelados de **Wave 1** (Fase 1) | 30/30 tests unitarios en verde + `[audit-ok]` en placeholders, extractores y enlaces. |
| **Wave 3** *(Integración CLI — Completada)* | **Fase 3** *(parte 2: Subcomandos y Cierre)* | **W3-A (Fase 3 — Init, Update, Bootstrap y Sync)**<br>**W3-B (Fase 3 — Entrypoint, Req, Check y Resolve)**<br>**W3-Audit (Gate solo lectura)** | **W3-A:** `cli/desktop_spec/commands/{init_cmd,update_cmd,bootstrap_cmd,sync_index_cmd}.py`, `cli/tests/test_update_and_brownfield.py`<br>**W3-B:** `cli/main.py`, `cli/desktop_spec/__main__.py`, `cli/desktop_spec/commands/{new_req_cmd,check_cmd,resolve_cmd}.py`, `dspec`, `dspec.ps1`, `cli/tests/test_cli_workflow.py` | **Wave 2** completa (Fase 2 + Fase 3 parte 1) | 41/41 tests en verde + `[audit-ok]` en contratos cruzados, cero emojis y stdlib puro. |
| **Wave 4** *(Pilotos, Guías y Release — Completada)* | **Fase 4** *(completa)* | **W4-A (Fase 4 — Piloto .NET Avalonia)**<br>**W4-B (Fase 4 — Piloto Python PySide6)**<br>**W4-C (Fase 4 — Guías Hub & Spoke + CI/Release)**<br>**W4-Audit (Gate solo lectura)** | **W4-A:** `examples/sample-dotnet-desktop/`<br>**W4-B:** `examples/sample-pyside6-desktop/`<br>**W4-C:** `guides/`, `README.md`, `CHANGELOG.md`, `scripts/bump_version.py`, `.github/workflows/{ci,release}.yml`, `cli/tests/test_packaging_and_e2e.py` | **Wave 3** completa (Fase 3 terminada) | Ambos pilotos pasan `dspec check --strict-tokens` sin advertencias + `45/45` tests y `bump_version.py --check` en verde. |
| **Wave 5** *(Extensión Híbridos — Completada)* | **Fase 5** *(completa)* | **W5-A (Fase 5 — Schemas, Detectores y CLI)**<br>**W5-B (Fase 5 — Templates IPC/FFI y Pilotos)**<br>**W5-Audit (Gate solo lectura)** | **W5-A:** `schemas/technical/`, `cli/desktop_spec/`, `cli/tests/`<br>**W5-B:** `templates/`, `examples/sample-tauri-desktop/`, `examples/sample-flutter-desktop/` | **Wave 4** completa | Retrocompatibilidad `v1.0.0` verificada, 4 pilotos sin advertencias y `53/53` tests en verde. |
| **Wave 6** *(Alineación Documental — Pendiente)* | **Fase 6** *(completa)* | **W6-A (Guías Hub & Spoke + README)**<br>**W6-B (Prompts, Skills y Config Template)**<br>**W6-C (Tests E2E y Anti-Doc-Drift)**<br>**W6-Audit (Gate solo lectura)** | **W6-A:** `guides/01..04`, `README.md`<br>**W6-B:** `agent-prompts/AGENTS.md`, `templates/.spec/config.yaml`, `templates/.spec/skills/**`<br>**W6-C:** `cli/tests/test_packaging_and_e2e.py` | **Wave 5** completa | Cero *doc drift* en guías/skills, 4/4 pilotos y `__version__` dinámico verificados + `[audit-ok]`. |
| **Wave 7** *(Endurecimiento CLI — Pendiente)* | **Fase 7** *(completa)* | **W7-A (Hardening `check_cmd`)**<br>**W7-B (Multi-Manifiesto `resolve` y `bootstrap` Wave 5)**<br>**W7-Audit (Gate solo lectura)** | **W7-A:** `cli/desktop_spec/commands/check_cmd.py`, `cli/tests/test_cli_workflow.py`<br>**W7-B:** `cli/desktop_spec/commands/{resolve_cmd,bootstrap_cmd}.py`, `cli/tests/test_update_and_brownfield.py` | **Wave 5** completa | Tests de regresión para `--staged`, `--strict-tokens`, multi-manifiesto y `bootstrap` en 16 perfiles en verde. |
| **Wave 8** *(Greenfield + Brownfield DX — Pendiente)* | **Fase 8** *(completa)* | **W8-A (Día 0 Greenfield + `--scaffold-specs`)**<br>**W8-B (Legados Planos, `docs/` previos y `--warn-only`)**<br>**W8-Audit (Gate solo lectura)** | **W8-A:** `cli/desktop_spec/commands/{init_cmd,update_cmd,new_req_cmd}.py`, `cli/tests/test_greenfield_dx.py`<br>**W8-B:** `cli/desktop_spec/commands/{bootstrap_cmd,sync_index_cmd,check_cmd}.py`, `cli/tests/test_brownfield_dx.py` | **Wave 7** completa | Flujos E2E Greenfield (`empty -> scaffold -> primer commit`) y Brownfield plano verificados al 100%. |
| **Wave 9** *(Guardrails Avanzados y Equipos — Pendiente)* | **Fase 9** *(completa)* | **W9-A (Seguridad Offline y Auditores Locales)**<br>**W9-B (Fronteras `UF/UC` e Imports Modulares)**<br>**W9-C (Backlog Multi-Archivo Anti-Colisión)**<br>**W9-Audit (Gate solo lectura)** | **W9-A:** `cli/desktop_spec/security/`, integración en `check_cmd.py`, `cli/tests/test_security_offline.py`<br>**W9-B:** `cli/desktop_spec/validator/boundary_checker.py`, `templates/.spec/templates/_template_arch_test.md`, `cli/tests/test_boundary_checker.py`<br>**W9-C:** `cli/desktop_spec/commands/{new_req_cmd,sync_index_cmd,resolve_cmd}.py`, `cli/tests/test_concurrent_backlog.py` | **Wave 8** completa | Tests positivos/negativos de secretos, fronteras y backlog concurrente pasando sin romper `v1.0.0`. |

---

## 3. Recomendación Práctica al Invocar `/teamwork` y Optimización de Modelos

Tanto `/teamwork` (`swarm`) como los subagentes directos heredan el modelo del agente padre por defecto. Para optimizar velocidad y consumo de cuota sin perder rigor:

- **Modelo Fuerte (Heredado):** Asignar a diseño de contratos/schemas, arquitectura CLI (`detector/`, `validator/`, `commands/`) y proyectos piloto.
- **Modelo Ligero (`Flash` — ej. `gemini-3.8-flash-medium` en `swarm` / `flash` en subagentes):** Asignar a auditores de solo lectura, verificación cruzada de placeholders/enlaces y validaciones mecánicas entre oleadas.
- **Resiliencia ante cuota:** En `swarm`, si un worker agota cuota durante una oleada larga, usar `action: "model"` para cambiarlo en caliente conservando su historial.

### Orden de Ejecución de Oleadas
1. **Wave 1 (Fase 1 — Completada):** 2 workers de diseño (`W1-A`, `W1-B`) con modelo heredado + 1 auditor (`W1-Audit`) con modelo `Flash`.
2. **Wave 2 (Fase 2 completa + Fase 3 parte 1 — Completada):** 5 workers en paralelo (`workspace: "inherit"`) + 1 auditor (`Flash`) validando 30/30 pruebas unitarias y paridad de los 22 placeholders.
3. **Wave 3 (Fase 3 parte 2 — integración CLI — Completada):** 2 workers (`W3-A`, `W3-B`) con propiedad disjunta + 1 auditor (`Flash`) validando 41/41 pruebas en verde (`init`, `update`, `bootstrap`, `req:new`, `sync`, `check`, `resolve`).
4. **Wave 4 (Fase 4 — Completada):** 3 workers en paralelo (`W4-A`, `W4-B`, `W4-C`) + 1 auditor (`Flash`) validando pilotos Avalonia/PySide6, guías y CI/Release (`45/45` tests).
5. **Wave 5 (Fase 5 — Completada):** 2 workers en paralelo (`W5-A`, `W5-B`) + 1 auditor (`Flash`) incorporando 5 perfiles híbridos/nativos adicionales y 2 pilotos (`53/53` tests).
6. **Wave 6 (Fase 6 — Pendiente):** 3 workers (`W6-A`, `W6-B`, `W6-C`) + 1 auditor (`Flash`) para erradicar el *doc drift* en guías/prompts/skills y blindar `test_packaging_and_e2e.py`.
7. **Wave 7 (Fase 7 — Pendiente):** 2 workers (`W7-A`, `W7-B`) + 1 auditor (`Flash`) para endurecer `--staged`, `--strict-tokens`, multi-manifiesto en `resolve --bump` y `bootstrap` Wave 5.
8. **Wave 8 (Fase 8 — Pendiente):** 2 workers (`W8-A`, `W8-B`) + 1 auditor (`Flash`) para pulir Día 0 Greenfield y adopción progresiva Brownfield.
9. **Wave 9 (Fase 9 — Pendiente):** 3 workers (`W9-A`, `W9-B`, `W9-C`) + 1 auditor (`Flash`) para seguridad offline, chequeo estático de fronteras y backlog concurrente anti-colisión.
