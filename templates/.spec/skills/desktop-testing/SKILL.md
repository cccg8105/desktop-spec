---
name: desktop-testing
description: "Piramide de verificacion nativa para monolitos modulares desktop: tests de arquitectura modular, dominio/SQLite, ViewModel/FSM, UI Headless/OS Automation, /diagnose en PATCH y auditoria de seguridad."
---

# desktop-testing Skill

Esta skill guia la validacion automatizada multi-nivel en `desktop-spec` sin servidor backend propio, cubriendo desde fronteras entre modulos hasta automatizacion visual nativa o WebView y accesibilidad del sistema operativo.

## Piramide de Verificacion Nativa (4 Niveles)

1. **Nivel 1 — Arquitectura Modular (`modular-architecture.md`):**
   - Verifica que ningun modulo `MOD-*` importe clases/paquetes internos de otro modulo ajeno y que las vistas/ViewModels no accedan directamente a SQLite o repositorios de infraestructura.
   - Herramientas segun ecosistema: `NetArchTest` (.NET), `import-linter` (Python), `ArchUnit` (JVM), visibilidad de crates/modulos en Rust/C++.
2. **Nivel 2 — Dominio, OCL y Persistencia Local (`.spec/templates/_template_domain_test.md`):**
   - Prueba casos de uso `UC-*`, reglas `[BR-XX]` e invariantes OCL (`pre`, `post`, `inv`) y excepciones tipadas `[EX-XX]`.
   - Usa bases SQLite en memoria o directorios temporales aislados para validar migraciones *on-startup*, respaldo previo del `.db`, rechazo de `schema_version` futuro, escritura atomica de archivos de proyecto, prevencion de Path Traversal y mocks de OS Keyring.
   - Runners: `xUnit`/`NUnit` (.NET), `pytest` (Python), `JUnit 5` (JVM), `cargo test` (Rust), `GoogleTest` (C++), `Vitest` / `cargo test` (Tauri), `Vitest` (Electron), `go test` (Wails), `flutter test` (Flutter), `XCTest` (Swift/macOS).
3. **Nivel 3 — ViewModel / Presenter / Maquina de Estados FSM:**
   - Verifica transiciones entre `Idle`, `Loading`/`Busy`, `Empty`, `Error` y `Dirty`, traduccion de excepciones `[EX-XX]` a mensajes legibles y cumplimiento de invariantes (`NoDoubleSubmit`, `PreserveDraftOnError`, `RollbackOnOptimisticFailure`, `NoMainThreadBlock` con `CancellationToken` / corrutinas, `GuardUnsavedChangesOnClose`).
4. **Nivel 4 — UI Headless, Automatizacion OS y Accesibilidad Nativa (`.spec/templates/_template_ui_test.md`):**
   - Ejecuta pruebas de interfaz en modo headless o automatizacion de escritorio segun ecosistema: `Avalonia.Headless` / `FlaUI` (.NET), `pytest-qt` (Python), `Compose UI Test` / `TestFX` (JVM), `Slint` test harness / `Qt Test` (Rust/C++), `tauri-driver` (Tauri), `Playwright (Electron)` (Electron), `go test` / WebDriver (Wails), `flutter test` / `integration_test` (Flutter), `XCTest` / `XCUITest` (Swift/macOS).
   - Valida geometria minima de ventana `WIN-*`, modos `light` / `dark` / `high-contrast`, navegacion completa por teclado (`Tab`, `Enter`, `Escape`, atajos `Ctrl` vs `Cmd`), `FocusRestoration` y roles/etiquetas de accesibilidad del SO (UI Automation / AT-SPI / NSAccessibility).

---

## Protocolo Spec-First y Fast-Track (`/diagnose`)
- **Trazabilidad:** Todo test nuevo debe incluir anotaciones `@spec`, `@req` y `@businessRule` o `@invariant` enlazando con `UC-*` / `UF-*` y `REQ-DESK-*`.
- **En `MAJOR` / `MINOR`:** Escribe los tests de dominio (`_template_domain_test.md`) y/o UI (`_template_ui_test.md`) en rojo antes de implementar.
- **En `PATCH` Fast-Track:** Aplica `/diagnose`:
  1. Reproduccion determinista del fallo.
  2. Aislamiento del caso minimo reproducible.
  3. Hipotesis explicita de causa raiz.
  4. Test de regresion automatizado en rojo antes de tocar codigo productivo.

## Auditoria de Seguridad de Dependencias (`gh` + Auditor Local)
Cuando el cambio atienda vulnerabilidades o actualice dependencias (`REQ-DESK-SEC-*`):
1. Verifica `gh auth status` y extrae alertas via `gh api "repos/{owner}/{repo}/dependabot/alerts?state=open"` y `gh pr list --author "app/dependabot"`.
2. Ejecuta el auditor local del ecosistema (`dotnet list package --vulnerable --include-transitive`, `pip-audit`, `cargo audit`, `./gradlew dependencyCheckAnalyze`, `npm audit`, `govulncheck`, `flutter pub outdated` / `dart pub outdated`).
3. Valida la suite completa de regresion y ejecuta `desktop-spec check --security` (o `dspec check --security`) antes de cerrar con `dspec resolve`.
