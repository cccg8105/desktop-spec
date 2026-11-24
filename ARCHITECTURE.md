# Arquitectura Base — desktop-spec

Este documento define los **componentes principales** de `desktop-spec`, los ecosistemas nativos priorizados para `v0.1.0 -> v1.0.0`, la **frontera estricta entre `UF-*` y `UC-*`**, y los límites explícitos de alcance del framework.

---

## 1. Principios de Diseño y Alcance

1. **Prioridad Nativa (*Native-First*):** La línea base `v1.0.0` gobierna aplicaciones nativas de proceso único donde la UI, la capa de presentación (MVVM/MVI), el dominio y la persistencia conviven en un mismo binario/paquete. Shells híbridos con WebView (Electron, Tauri, Wails) se reservan para una fase posterior (`v1.1+`) sin contaminar los contratos nativos iniciales.
2. **Especialización Desktop (*Standalone / Local-First*):** El framework cubre aplicaciones autocontenidas sin servidor backend propio ni sincronización cloud distribuida (alcance reservado para un futuro framework full-stack).
3. **Monolito Modular con Fronteras Verificables:** El mayor riesgo técnico en desktop no es la latencia de red, sino la erosión arquitectónica interna (vistas llamando directo a SQL o módulos acoplándose a internos ajenos). `desktop-spec` trata los **Módulos de Dominio** y sus **fachadas públicas** como ciudadanos de primera clase.
4. **Pilares Transversales de Gobernanza:** El framework se apoya en 5 pilares deterministas:
   - Fuente Única de Verdad (`docs/`) separada de los moldes del agente (`.spec/templates/`).
   - Protocolo Gatekeeper de Dos Velocidades (`MAJOR`/`MINOR` Carril Completo vs. `PATCH` Fast-Track con `/diagnose`).
   - Guardrails deterministas en Python `>=3.9` stdlib (`schemas/` Draft-07, Rolling Window `<= 3` filas, hook `pre-commit --staged`, `check --security` con `gh`).
   - Onboarding Brownfield con `.spec/bootstrap-report.md`, expansión progresiva *Just-In-Time* y buzón de solo lectura `docs/backlog/audit-proposals.md`.
   - Multi-harness (Antigravity, Claude Code, Cursor, Windsurf) con marcadores `DESKTOP-SPEC:START/END` y actualización incremental con `graphify`.

---

## 2. Ecosistemas Nativos Priorizados (`v1.0.0`)

| Familia | Perfiles Objetivo | Manifiesto Principal | Capa UI / Patrón Típico | Herramientas de Testing Base |
| :--- | :--- | :--- | :--- | :--- |
| **.NET Desktop** | `wpf`, `winui3`, `avalonia`, `maui-desktop` | `*.csproj` | XAML / MVVM (`CommunityToolkit.Mvvm`, ReactiveUI) | `xUnit` / `NUnit` + `Avalonia.Headless` / `FlaUI` |
| **Python Desktop** | `pyside6`, `pyqt6`, `flet` | `pyproject.toml` / `setup.cfg` | Qt Widgets / QML / MVVM-MVP | `pytest` + `pytest-qt` |
| **JVM Desktop** | `compose-desktop`, `javafx` | `build.gradle.kts` / `build.gradle` / `pom.xml` | Compose / FXML + StateFlow / MVI-MVVM | `JUnit 5` + Compose UI Test / `TestFX` |
| **Rust / C++ Nativos** | `rust-native` (`slint`, `iced`, `egui`), `qt-cpp` (`Qt6`) | `Cargo.toml` / `CMakeLists.txt` | Declarativo nativo / Qt Quick / Elm-like | `cargo test` / `GoogleTest` + `Qt Test` |

---

## 3. Frontera Estricta Funcional: `UF-*` vs. `UC-*`

En un monolito modular desktop, mantener separados los flujos de interfaz (`docs/functional/user-flows/UF-*.md`) de los casos de uso de dominio (`docs/functional/use-cases/UC-*.md`) evita sobrecargar un solo documento, siempre que exista una **frontera de delegación unidireccional**:

> **Regla de Oro de Frontera:** `UF-*` describe **cómo interactúa el usuario con ventanas, controles y atajos** y delega las mutaciones de negocio a un `UC-*`. `UC-*` describe **qué reglas de negocio, invariantes OCL y persistencia local ejecuta el módulo** sin conocer ventanas, botones ni toolkits UI.

### Matriz de Responsabilidades (Cero Redundancia, Cero Contradicción)

| Dimensión | `UF-*` (`docs/functional/user-flows/`) | `UC-*` (`docs/functional/use-cases/`) |
| :--- | :--- | :--- |
| **Capa que gobierna** | Presentación (`Views`, `Windows`, `Dialogs`, `ViewModels/Presenters`, UI FSM). | Aplicación y Dominio del Módulo (`UseCases`, `CommandHandlers`, `Entities`, `Domain Events`, `Ports`). |
| **Contenido obligatorio / propio** | - Ventana/vista origen y modal/panel destino.<br>- Disparador de usuario (clic, atajo `Ctrl+S`, menú, drag-and-drop).<br>- Validación de formato inmediata en campo (máscaras, campos vacíos).<br>- Matriz de estados UI (`Loading`, `Empty`, `Error`, `Busy/Cancellable`).<br>- Máquina de estados UI (`stateDiagram-v2`) e invariantes (`NoDoubleSubmit`, `NoMainThreadBlock`, `GuardUnsavedChangesOnClose`, `FocusRestoration`).<br>- Accesibilidad nativa (orden de tabulación, roles/etiquetas OS UI Automation/AT-SPI/NSAccessibility) y geometría mínima de ventana.<br>- **Referencia explícita de delegación:** `invokes_use_case: UC-DOM-XXX` (si aplica). | - Actor o módulo invocador y precondiciones de dominio.<br>- Diagrama de flujo/decisión de negocio.<br>- Contrato de entrada/salida en DTOs agnósticos de UI.<br>- Reglas de negocio `[BR-XX]` con **OCL heurístico** (`pre`, `post` con `@pre`, `inv`) en cálculos, estados o restricciones multi-campo.<br>- Efectos en persistencia local (SQLite/WAL, archivos de proyecto, OS Keyring) o eventos publicados en el Event Bus interno.<br>- Excepciones tipadas de dominio (`[EX-XX]`) que la UI traducirá a feedback legible. |
| **Contenido PROHIBIDO** | - **Prohibido** redactar fórmulas de negocio, invariantes OCL de entidades, nombres de tablas SQLite ni detalles de repositorios.<br>- Si hay cálculo o transición de entidad, solo enlaza al `UC-*`. | - **Prohibido** mencionar botones, colores, diálogos modales, skeletons, atajos de teclado, `ViewModel` o widgets de WPF/Qt/Compose.<br>- Si una regla falla, devuelve un error de dominio tipado, no un "toast rojo". |
| **Cuándo se omite** | En requerimientos puramente internos: migraciones automáticas, workers de mantenimiento, indexación en background o lógica batch sin cambios en pantallas (`uc_only`). | En flujos puramente presentacionales o de navegación sin reglas de negocio ni persistencia de dominio (ej. cambio de tema claro/oscuro, layout de paneles, diálogo "Acerca de") (`uf_only`). |

### Vinculación en `docs/backlog/pending.md` (`REQ-DESK-*`)

- Todo `REQ-DESK-*` con impacto `MAJOR` o `MINOR` declara en `references`:
  - `user_flows`: lista de `UF-*.md` afectados (opcional solo si `uc_only`).
  - `use_cases`: lista de `UC-*.md` afectados (opcional solo si `uf_only`).
  - Al menos uno de los dos debe existir físicamente en disco; ambos pueden convivir cuando un cambio abarca interacción + dominio.
- Solo `PATCH` (*Fast-Track*) admite `N/A (PATCH / Fast-Track)`.

---

## 4. Los 5 Componentes Principales de `desktop-spec`

### Componente 1 — Contratos Funcionales Duales (`docs/functional/` + `schemas/`)
- **`schemas/user-flow.schema.json`:** Valida `UF-[DOMINIO]-[NUM]`, `window_target`, `shortcut`, `invokes_use_case`, estados UI (`Loading`/`Empty`/`Error`/`Busy`), FSM e invariantes nativos de accesibilidad/geometría.
- **`schemas/use-case.schema.json`:** Valida `UC-[DOMINIO]-[NUM]`, DTOs entrada/salida, reglas `[BR-*]` con OCL opcional, efectos en BD local/archivos/Event Bus y excepciones de dominio.
- **`docs/functional/index.md`:** Catálogo sincronizado de `UF-*`, `UC-*` y módulos legados pendientes *As-Is* (`Brownfield Just-In-Time`).

### Componente 2 — Sistema de Diseño Nativo y Tokens (`docs/design/` + `schemas/design/`)
- **`docs/design/tokens-and-themes.md` + `schemas/design/tokens-and-themes.schema.json`:**
  - Modos obligatorios `light`, `dark` (y soporte `system` / `high-contrast` del SO).
  - Paleta semántica acotada, tipografía del sistema/embebida, escala de espaciado y **densidad desktop** (compacta/estándar para herramientas con alta carga de datos).
  - Exportación opcional en formato neutro **W3C DTCG** (`*.tokens.json`) pensada para generar recursos nativos (XAML `ResourceDictionary`, Qt `.qss`, Compose `Theme`), evitando acoplar el núcleo a CSS/Tailwind.

### Componente 3 — Pilares Técnicos del Monolito Modular (`docs/technical/` + `schemas/technical/`)
Cada proyecto consumidor mantiene 5 documentos técnicos verificables contra JSON Schema Draft-07:

1. **`tech-stack.md`:** Ecosistema nativo (`wpf`, `avalonia`, `pyside6`, `compose-desktop`, `qt-cpp`, `rust-native`, etc.), toolkit UI, BD embebida, OS Keyring, suite de pruebas unitarias y UI headless, **Presupuestos Desktop** (`cold_startup_ms`, `idle_ram_mb`, `ui_frame_budget_ms <= 16`, `installer_max_mb`) y políticas de seguridad local (deserialización segura, prevención de *Path Traversal*, prohibición de secretos hardcodeados en binario).
2. **`modular-architecture.md`:** Define la estructura del **Monolito Modular**:
   - Mapa de **Módulos de Dominio** (`MOD-*`), sus fachadas/puertos públicos y reglas de dependencia acíclica (prohibición de imports cruzados entre internos de módulos).
   - Capas por módulo (`Presentation/ViewModel`, `Application/UseCases`, `Domain`, `Infrastructure`).
   - **Event Bus en memoria** para desacoplar módulos sin red HTTP.
   - Modelo de concurrencia **UI Thread vs. Background Workers** (`CancellationToken` / corrutinas / `QThread` / `tokio`).
3. **`windowing-and-os-contracts.md`:** Especifica la gestión de ventanas e integraciones nativas del sistema operativo:
   - Topología de ventanas (Single-Window vs. Multi-Window, diálogos modales/no modales, *System Tray*, política *Single-Instance Lock*).
   - Mapa de comandos globales, menús nativos, atajos de teclado y guardia de cierre (`unsaved-changes guard`).
   - Contratos con el SO: diálogos de archivos, *Drag & Drop*, asociaciones de extensión (`.ext`), argumentos CLI, *Deep Links* locales y permisos/capacidades del SO.
4. **`local-persistence.md`:** Documenta el almacenamiento local y ciclo de migraciones:
   - Esquema relacional/documental embebido (SQLite/WAL/SQLCipher, DuckDB, archivos de proyecto) con diagrama `erDiagram`.
   - Rutas estándar del SO (`%APPDATA%`, `~/Library/Application Support`, `$XDG_DATA_HOME`) separando datos, caché y logs rotativos.
   - Política obligatoria de **migraciones automáticas *on-startup***: idempotencia, **snapshot/backup previo del `.db`**, y verificación de compatibilidad `schema_version` ante archivos creados por versiones futuras.
5. **`packaging-and-release.md`:** Gobierna la construcción multiplataforma y distribución del binario:
   - Pipeline CI en matriz multi-SO (`windows-latest`, `macos-latest`, `ubuntu-latest`).
   - Empaquetado nativo (`MSIX`/`WiX`/`InnoSetup`, `.dmg`/`.pkg`, `AppImage`/Flatpak/DEB).
   - **Code Signing & Notarization** (certificados en `secrets.*`, nunca versionados), generación de hashes SHA-256, canales de actualización (`stable`/`beta`), **Auto-Updater** y recuperación local ante fallos.

### Componente 4 — Gobernanza, Prompts, Skills y Multi-Harness (`agent-prompts/`, `harnesses/`, `templates/`)
- **Prefijos propios anti-colisión:** `REQ-DESK-*`, `AUDIT-DESK-*`, comandos `/desk-bootstrap`, `/desk-grill`, `/desk-plan`, `/desk-resolve`, `/desk-execute`, y marcadores `<!-- DESKTOP-SPEC:START/END -->` y `# DESKTOP-SPEC:START/END`.
- **Skills bajo demanda en `.spec/skills/`:**
  - `desktop-spec` (orquestador Gatekeeper de Dos Velocidades).
  - `desktop-spec-bootstrap` (descubrimiento Brownfield en 4 fases).
  - `desk-grill` (entrevista socrática "Código, Módulos y Esquemas primero").
  - `desktop-testing` (pirámide nativa: tests de arquitectura modular + dominio/SQLite + ViewModel + UI Headless/Automation).
  - `desktop-release` (matriz CI multi-SO, *Code Signing*, *Auto-Updater*, variables/secretos `gh` y corte de tag `vX.Y.Z`).

### Componente 5 — Motor CLI Determinista (`cli/desktop_spec/`)
- Paquete Python `>=3.9` sin dependencias externas (`stdlib`), instalable vía `uv`/`pipx`/`hatchling` con binarios `desktop-spec` y `dspec`.
- **7 subcomandos:** `init`, `update`, `bootstrap`, `req:new`, `sync`, `check`, `resolve`.
- **Capacidades especializadas para escritorio nativo:**
  - `req:new` soporta `--uc`, `--uf` o ambos (`--scope {ui-only,domain-only,full-module,packaging-infra}`), y asigna artefactos según el ecosistema nativo (`View` + `ViewModel` + `UseCase` + Tests).
  - `check` valida consistencia entre `UF-*` -> `UC-*` (verificando que `invokes_use_case` exista y que las fronteras de módulo no se violen en `--staged`), además de extensiones nativas (`.cs`, `.xaml`, `.py`, `.kt`, `.java`, `.rs`, `.cpp`, `.hpp`, `.h`, `.qml`, `.ui`, `.axaml`).
  - `bootstrap` inventaría módulos/paquetes del monolito, ventanas/vistas, ViewModels, modelos/migraciones locales y archivos de build/signing.

---

## 5. Fronteras Explícitas de Alcance (`v1.0.0`)

| Dimensión | Incluido en `desktop-spec` (`v1.0.0`) | Fuera de Alcance (Excluido por Diseño) |
| :--- | :--- | :--- |
| **Gobernanza y Runtime CLI** | Dos Velocidades, `pending.md`/`changelog.md`/`audit-proposals.md`, Rolling Window (`<= 3`), Draft-07 sin deps, `--staged`, `--security` (`gh`), `--refresh-stack`, `--ci github`, Graphify, Multi-Harness y runtime puro en Python `>=3.9` stdlib. | Dependencias de terceros en el motor CLI o requerimiento de runtimes web (Node/npm) para operar la gobernanza. |
| **Dominio y Persistencia** | Monolito modular Clean/Hexagonal, Casos de Uso `UC-*` + OCL heurístico, `erDiagram` y migraciones *on-startup*, pruebas *Spec-First* de dominio/BD, extractor multi-manifiesto (`xml`, `toml`, `gradle`, `cfg`, `cmake`, `plain`, `json`). | Infraestructura de servidores remotos: Dockerfiles multi-stage, Kubernetes probes (`/health/live`, `/health/ready`), rollout `canary`/`blue_green`, endpoints REST/gRPC obligatorios, RFC 7807 HTTP, Rate Limiting, RBAC multi-tenant, Kafka/Redis/DLQ. |
| **Interfaz y Experiencia Nativa** | Flujos `UF-*` + Matriz FSM (`NoDoubleSubmit`, `PreserveDraftOnError`, `FocusRestoration`, `NoMainThreadBlock`, `GuardUnsavedChangesOnClose`), Design Tokens claro/oscuro/alto-contraste + W3C DTCG, densidad desktop y accesibilidad OS nativa. | Métricas y artefactos exclusivos web: Web Vitals (`LCP`, `INP`, `CLS`), `bundle_max_kb`, SEO, SSR/SSG/ISR/RSC, Mobile-First (`390x844`), `Cache-Control` CDN, `VITE_*`/`NEXT_PUBLIC_*`, `axe-core` DOM, Playwright web o MSW HTTP. |
