# Instrucciones Canonicas para Agentes de IA (`desktop-spec` v{{FRAMEWORK_VERSION}})

Este proyecto implementa la metodologia **`desktop-spec` v{{FRAMEWORK_VERSION}}** para aplicaciones de escritorio **nativas** estructuradas como **monolito modular standalone** (sin servidor backend propio ni WebView en `v1.0`), con soporte multi-ecosistema (`.NET`: `wpf`, `winui3`, `avalonia`, `maui-desktop`; `Python`: `pyside6`, `pyqt6`, `flet`; `JVM`: `compose-desktop`, `javafx`; `Rust / C++`: `rust-native`, `qt-cpp`) y compatibilidad multi-harness (Antigravity, Claude Code, Cursor, Windsurf). El agente actua como Arquitecto Desktop e Ingeniero de Software gobernando el ciclo de vida mediante el **Protocolo Gatekeeper de Dos Velocidades**.

> **Nota de Entorno / Harness:** En `Claude Code`, `Cursor` y `Windsurf`, utiliza los comandos `/desk-grill`, `/desk-plan`, `/desk-bootstrap` y `/desk-resolve` (o `/desk-execute` en Windsurf). En `Antigravity`, utiliza los slash nativos `/grill-me`, `/plan`, `/diagnose` y `/code-review`. Las reglas especificas del harness viven bajo el bloque `<!-- DESKTOP-SPEC:START -->`..`<!-- DESKTOP-SPEC:END -->`.

---

## PROTOCOLO GATEKEEPER DE DOS VELOCIDADES

### REGLA DE ORO: PROHIBIDO CODIFICAR SIN REQUERIMIENTO EN EL BACKLOG
**Nunca modifiques codigo fuente (`src/`, `modules/`, `views/`, `ui/`, `tests/`) sin que exista un requerimiento `REQ-DESK-*` registrado en `docs/backlog/pending.md` y aprobado explicitamente por el usuario.**
**Solo lectura de auditoria:** Trata `docs/backlog/audit-proposals.md` (`[AUDIT-DESK-*]`) como buzon de triage de solo lectura; nunca implementes cambios desde alli sin promoverlos antes a `docs/backlog/pending.md`.

Ante cualquier solicitud del usuario, clasifica primero su impacto segun `docs/backlog/versioning-strategy.md`:

| Tipo de Cambio | Impacto | Carril Activado | Ceremonia Requerida |
| :--- | :--- | :--- | :--- |
| Nuevas funcionalidades, ventanas `WIN-*`, modulos `MOD-*`, cambios de contratos `UF-*`/`UC-*`, tokens o upgrade `MAJOR` que altere codigo fuente | `MAJOR` / `MINOR` | **Carril Completo** | Entrevista (`/desk-grill` o `/grill-me`) -> Frontera Funcional (`UF-*` y/o `UC-*`) -> Tokens/Arquitectura Modular/Ventanas y Persistencia/Empaquetado -> Tests *Spec-First* -> `docs/backlog/pending.md` -> Gatekeeper `/plan` (`/desk-plan`). |
| Bug local sin alterar contratos de dominio, ni esquemas SQLite/archivos, ni firmas de fachadas, ni ventanas nuevas; o parche de seguridad Dependabot compatible | `PATCH` | **Carril Fast-Track (Micro-Spec)** | Omite crear `UF-*` o `UC-*` nuevos (`N/A (PATCH / Fast-Track)`). Registra bloque compacto `REQ-DESK-* (PATCH)` en `pending.md` (ej. `REQ-DESK-SEC-*`), aplica `/diagnose` + test de regresion en rojo, pide confirmacion breve y aplica el fix minimo. |

---

## FRONTERA ESTRICTA FUNCIONAL (`UF-*` VS. `UC-*`)

Consulta `.spec/templates/functional-boundary-guidelines.md` antes de crear especificaciones funcionales. La dependencia es **unidireccional**:

- **Escenario Dual (`scope: full-module`):** `UF-*` gobierna ventana/dialogo (`window_target`), atajos, estados UI (`Idle`, `Busy`, `Empty`, `Error`, `Dirty`), FSM e invariantes nativos, y delega mediante `invokes_use_case: UC-[MOD]-[NUM]`. `UC-*` gobierna DTOs de entrada/salida, reglas `[BR-XX]` con OCL heuristico, persistencia local (SQLite/WAL, archivos de proyecto, OS Keyring), eventos internos y excepciones tipadas `[EX-XX]`.
- **Solo Dominio (`scope: domain-only` / `uc-only`):** Procesos internos sin cambios en pantalla (migraciones on-startup, workers en segundo plano, indexacion, watchers). Usa `UC-*` y deja `user_flows: []`.
- **Solo Interfaz (`scope: ui-only` / `uf-only`):** Flujos puramente presentacionales o ergonomicos (cambio de tema, densidad, docking de paneles, dialogo Acerca de). Usa `UF-*` con `invokes_use_case: N/A` y deja `use_cases: []`.
- **Prohibido cruzar la frontera:** Ningun `UF-*` debe incluir formulas de negocio, OCL de entidades ni SQL/tablas; ningun `UC-*` debe mencionar ventanas, botones, colores ni widgets de toolkit.

---

## FLUJO DEL CARRIL COMPLETO (`MAJOR` / `MINOR`)

### Paso 1: Diagnostico y Entrevista (`{{HARNESS_INTERVIEW_TRIGGER}}`)
1. Consulta `docs/functional/index.md`, `docs/design/index.md` y `docs/technical/index.md` cargando unicamente los artefactos afectados (Contexto Selectivo O(1)).
2. Inspecciona primero codigo fuente, modulos, esquemas locales y `graphify-out/` si existe (*Codigo, Modulos y Esquemas primero, humano despues*).
3. Si persisten ambiguedades, despeja decisiones de frontera `UF -> UC`, invariantes UI/OCL, concurrencia (UI Thread vs Background Workers), persistencia local y contratos del SO.

### Paso 2: Especificacion Viva, Tokens y Pilares Tecnicos
1. **Funcional (`01a_plan_use_case` / `01b_plan_user_flow`):**
   - Crea o actualiza `docs/functional/use-cases/UC-[MOD]-[NUM]-[slug].md` (`.spec/templates/_template_use_case.md`) cuando haya reglas de negocio o persistencia local.
   - Crea o actualiza `docs/functional/user-flows/UF-[MOD]-[NUM]-[slug].md` (`.spec/templates/_template_user_flow.md`) cuando haya interaccion de usuario o ventana, aplicando la Matriz Heuristica FSM (`.spec/templates/ui-contracts-guidelines.md`).
2. **Diseno Nativo (`02a_plan_tokens_and_themes`):** Actualiza `docs/design/tokens-and-themes.md` (`.spec/templates/_template_design_tokens.md` y `design-guidelines.md`) manteniendo modos `light`, `dark`, `system` y `high-contrast`, densidad desktop (`compact`, `standard`, `comfortable`) y mapeo nativo (XAML/QSS/Compose/Slint).
3. **Arquitectura Modular (`02b_plan_modular_architecture`):** Actualiza `docs/technical/modular-architecture.md` declarando modulos `MOD-*`, fachadas publicas, dependencia aciclica, Event Bus en memoria y modelo de concurrencia UI Thread vs Background Workers.
4. **Ventanas, SO y Persistencia (`02c_plan_windowing_and_persistence`):** Actualiza `docs/technical/windowing-and-os-contracts.md` (`WIN-*`, single-instance lock, atajos Win/Linux/macOS, integraciones OS) y `docs/technical/local-persistence.md` (SQLite WAL/SQLCipher/DuckDB, rutas estandar del SO, migraciones on-startup con respaldo previo).
5. **Presupuestos, Seguridad Local y Empaquetado (`02d_plan_packaging_release`):** Actualiza `docs/technical/tech-stack.md` (`cold_startup_ms`, `idle_ram_mb`, `ui_frame_budget_ms`, `installer_max_mb`, OS Keyring, Path Traversal, deserializacion segura) y `docs/technical/packaging-and-release.md` (matriz CI `windows-latest`/`macos-latest`/`ubuntu-latest`, Code Signing, Auto-Updater).
6. **Historial Rolling Window:** Manten `## Historial de Revisiones (Ultimos Cambios)` con un maximo de **3 filas** por documento.

### Paso 3: Backlog, Tests Spec-First y Gatekeeper (`/plan`)
1. Registra `[REQ-DESK-DOMINIO-XXX]` en `docs/backlog/pending.md` siguiendo `agent-prompts/commands/03_create_requirement.md` y ejecuta `dspec sync` y `dspec check`.
2. Genera los esqueletos de prueba *Spec-First* en rojo usando `.spec/templates/_template_domain_test.md` y/o `.spec/templates/_template_ui_test.md`.
3. Presenta el plan acotado a las fronteras del `REQ-DESK-*` y **deten la ejecucion hasta recibir aprobacion explicita**.

---

## FLUJO DEL CARRIL FAST-TRACK (`PATCH` / Hotfix)
1. Verifica que el cambio no altera contratos `UF-*`/`UC-*`, esquemas de persistencia, firmas de fachadas `MOD-*` ni topologia de ventanas `WIN-*`.
2. Registra el bloque compacto `REQ-DESK-[DOMINIO]-[XXX]` en `docs/backlog/pending.md` con `Referencia Funcional: N/A (PATCH / Fast-Track)` y ejecuta `dspec sync`.
3. Solicita confirmacion breve listando los archivos exactos a modificar.
4. Ejecuta `/diagnose` (reproduccion determinista, aislamiento minimo, hipotesis de causa raiz), escribe el test de regresion en rojo y aplica la correccion minima.

---

## EXPANSION PROGRESIVA BROWNFIELD (Just-In-Time)
Si una solicitud toca un modulo listado en `docs/functional/index.md` bajo `Modulos Legados Detectados (Pendiente As-Is)`:
1. Documenta primero su comportamiento *As-Is* (`status: "As-Is (Brownfield)"`) en `UC-*` y/o `UF-*` (con test de caracterizacion si no hay cobertura).
2. Registra deuda arquitectonica, visual o de seguridad local detectada en `docs/backlog/audit-proposals.md` (`[AUDIT-DESK-DOMINIO-NUM]`) sin alterar codigo fuera de alcance.
3. Planifica entonces la evolucion *To-Be* bajo el Carril Completo.

---

## SEGURIDAD LOCAL Y DEPENDABOT (`gh` CLI)

### 1. Higiene de Seguridad Local en Apps Nativas
- **OS Keyring:** Todo secreto de usuario o token se guarda en el almacen seguro del sistema operativo (Windows Credential Manager, macOS Keychain, Linux Secret Service); prohibido guardar credenciales en archivos planos o embeber secretos en el binario.
- **Path Traversal:** Toda ruta de archivo recibida desde dialogos, drag-and-drop, CLI o archivos de proyecto debe canonizarse y validarse contra el directorio permitido antes de abrir o escribir.
- **Deserializacion Segura:** Rechaza formatos binarios inseguros o polimorfismo sin lista blanca al cargar archivos de proyecto y preferencias.

### 2. Auditoria y Remediacion de Vulnerabilidades (Dependabot + `gh`)
1. **Pre-vuelo `gh`:** Ejecuta `gh auth status` y resuelve el repositorio (`gh repo view --json nameWithOwner -q .nameWithOwner`). Si `gh` no esta disponible o autenticado, indica `gh auth login` / `gh auth refresh -s security_events` y usa directamente el auditor local del ecosistema.
2. **Extraccion de Alertas:** Consulta `gh api "repos/{owner}/{repo}/dependabot/alerts?state=open&per_page=100"` (priorizando `critical` y `high`), revisa `gh pr list --author "app/dependabot" --state open` y corre el auditor local segun ecosistema:
   - `.NET`: `dotnet list package --vulnerable --include-transitive`
   - `Python`: `pip-audit`
   - `JVM`: `./gradlew dependencyCheckAnalyze` o plugin equivalente de dependencias
   - `Rust`: `cargo audit`
3. **Clasificacion:**
   - Parche SemVer compatible o actualizacion de lockfile sin cambios de API -> **Fast-Track (`PATCH`)** bajo `REQ-DESK-SEC-XXX`.
   - Upgrade `MAJOR` con impacto en codigo fuente o contratos -> escala a **Carril Completo (`/plan` / `/desk-plan`)**.
4. **Verificacion y Cierre:** Ejecuta el auditor local limpio, corre la suite unitaria/UI, valida con `desktop-spec check --security` (o `dspec check --security`) y cierra con `dspec resolve REQ-DESK-SEC-XXX --bump`.

---

## CICLO OBLIGATORIO DE REVISIÓN Y GRAPHIFY
1. **Antes de Editar:** Si existe `graphify-out/graph.json`, consulta nodos y acoplamientos entre modulos (`graphify query` / `graphify path`).
2. **Al Finalizar Tests:** Revisa el diff (`/code-review`) verificando fronteras `MOD-*`, uso estricto de tokens, ausencia de bloqueos en el hilo UI (`NoMainThreadBlock`) y cumplimiento de criterios, y ejecuta `graphify update` respetando `.graphifyignore`.
