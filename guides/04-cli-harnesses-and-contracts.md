# Guía 04: Referencia de CLI, Harnesses y Contratos

Referencia técnica de los 7 subcomandos de `desktop-spec` (`dspec`), los 16 ecosistemas soportados, los 9 esquemas JSON Schema Draft-07 y los 4 adaptadores de IDE/CLI.

> Anterior: [Guía 03: Flujo Diario en Dos Velocidades](03-daily-workflow-two-speeds.md) | Hub: [README.md](../README.md)

---

## 1. Subcomandos del CLI (7)

| Subcomando | Función principal |
| :--- | :--- |
| `init` | Inicializa `.spec/`, `docs/`, `.gitignore`, `.graphifyignore`, harnesses y hook `pre-commit` en proyectos greenfield o brownfield (`--ecosystem`, `--mode`, `--ci`). |
| `update` | Actualiza blueprints, skills y reglas gestionadas sin sobrescribir `docs/` viva ni reglas personalizadas; soporta `--refresh-stack`, `--ci` y `--dry-run`. |
| `bootstrap` | Escanea un proyecto existente (Brownfield), genera `.spec/bootstrap-report.md` (checklist GPS de 4 fases con preservación de `[x]` y `--reset`), actualiza `SYNC:TECH_STACK` y `modules:`, alimenta `PENDING_MODULES` y asegura `docs/backlog/audit-proposals.md`. |
| `req:new` | Crea un requerimiento `REQ-DESK-*` autogenerado en `docs/backlog/pending.md` (`--impact MAJOR|MINOR|PATCH`, `--module`, `--scope`, `--fast-track` o `--from-audit AUDIT-DESK-*`). |
| `sync` | Sincroniza `docs/backlog/index.md`, `docs/functional/index.md` y `docs/design/index.md`; con `--export-tokens` exporta `docs/design/tokens-and-themes.md` a `.spec/specs/design.tokens.json` (W3C DTCG). |
| `check` | Valida enlaces, esquemas JSON Draft-07, diagramas Mermaid, Rolling Window (`<= 3` filas en historial de revisiones) y commits staged (`--staged`, `--strict-tokens`, `--security`). |
| `resolve` | Retira un `REQ-DESK-*` de `pending.md`, lo archiva en `docs/backlog/changelog.md`, sincroniza índices y con `--bump` actualiza el manifiesto y `.spec/config.yaml` con protección anti-downgrade (`--force-version`). |

---

## 2. Ecosistemas Soportados (16)

Todos los perfiles residen en `ECOSYSTEM_PROFILES` y pueden detectarse automáticamente o fijarse con `dspec init --ecosystem <id>`:

| Identificador | Stack / Framework | Lenguaje | Manifiesto principal |
| :--- | :--- | :--- | :--- |
| `wpf` | WPF (.NET) | C# | `*.csproj` |
| `winui3` | WinUI 3 (Windows App SDK) | C# | `*.csproj` |
| `avalonia` | Avalonia UI (.NET) | C# | `*.csproj` |
| `maui-desktop` | .NET MAUI Desktop | C# | `*.csproj` |
| `pyside6` | PySide6 (Qt for Python) | Python | `pyproject.toml` |
| `pyqt6` | PyQt6 (Qt for Python) | Python | `pyproject.toml` |
| `flet` | Flet Desktop (Python) | Python | `pyproject.toml` |
| `compose-desktop` | Compose Multiplatform Desktop (JVM) | Kotlin | `build.gradle.kts` |
| `javafx` | JavaFX (JVM) | Java | `build.gradle.kts` / `pom.xml` |
| `rust-native` | Rust Native (Slint / Iced / egui) | Rust | `Cargo.toml` |
| `qt-cpp` | Qt6 (C++ / CMake) | C++ | `CMakeLists.txt` |
| `tauri` | Tauri (Rust + WebView) | Rust / TypeScript | `src-tauri/Cargo.toml` |
| `electron` | Electron (Node.js + Chromium) | TypeScript / Node.js | `package.json` |
| `wails` | Wails (Go + WebView) | Go / TypeScript | `wails.json` |
| `flutter-desktop` | Flutter Desktop | Dart | `pubspec.yaml` |
| `swift-macos` | SwiftUI / AppKit (macOS) | Swift | `Package.swift` |

---

## 3. Contratos JSON Schema Draft-07 (9)

Todos los esquemas residen en `schemas/` y se validan con el motor interno sin dependencias externas:

1. `schemas/requirement.schema.json` — Estructura y metadatos de requerimientos `REQ-DESK-*`.
2. `schemas/use-case.schema.json` — Frontmatter y secciones obligatorias de casos de uso `UC-*`.
3. `schemas/user-flow.schema.json` — Frontmatter y secciones obligatorias de flujos de ventana `UF-*`.
4. `schemas/design/tokens-and-themes.schema.json` — Contrato de `docs/design/tokens-and-themes.md` y tokens de diseño.
5. `schemas/technical/tech-stack.schema.json` — Contrato de `docs/technical/tech-stack.md`.
6. `schemas/technical/modular-architecture.schema.json` — Contrato de `docs/technical/modular-architecture.md` (Bounded Contexts y fronteras).
7. `schemas/technical/windowing-and-os-contracts.schema.json` — Contrato de `docs/technical/windowing-and-os-contracts.md` (ventanas y contratos del SO).
8. `schemas/technical/local-persistence.schema.json` — Contrato de `docs/technical/local-persistence.md` (SQLite/WAL, migraciones y respaldos).
9. `schemas/technical/packaging-and-release.schema.json` — Contrato de `docs/technical/packaging-and-release.md` (empaquetado, firma y auto-actualización).

---

## 4. Adaptadores de Harnesses (4)

`desktop-spec` distribuye reglas, comandos/workflows y skills gestionados para:

- `antigravity` — Google Antigravity (`.gemini/rules/desktop-spec.md`, `.gemini/skills/`)
- `claude` — Claude Code (`CLAUDE.md`, `.claude/commands/`, `.claude/skills/`)
- `cursor` — Cursor (`.cursor/rules/desktop-spec.mdc`, `.cursor/commands/`, `.cursor/skills/`)
- `windsurf` — Windsurf (`.windsurfrules` en la raíz, `.windsurf/workflows/`, `.windsurf/skills/`)
