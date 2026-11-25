# Guía 04: Referencia de CLI, Harnesses y Contratos

Referencia técnica de los 7 subcomandos de `desktop-spec` (`dspec`), los 11 ecosistemas nativos soportados, los 9 esquemas JSON Schema Draft-07 y los 4 adaptadores de IDE/CLI.

> Anterior: [Guía 03: Flujo Diario en Dos Velocidades](03-daily-workflow-two-speeds.md) | Hub: [README.md](../README.md)

---

## 1. Subcomandos del CLI (7)

| Subcomando | Función principal |
| :--- | :--- |
| `init` | Inicializa `.spec/`, `docs/`, `.gitignore`, `.graphifyignore`, harnesses y hook `pre-commit` en proyectos greenfield o brownfield. |
| `update` | Actualiza blueprints y reglas gestionadas sin sobrescribir `docs/` viva ni reglas personalizadas; soporta `--refresh-stack` y `--dry-run`. |
| `bootstrap` | Escanea un proyecto existente, inventaria dominios/ventanas/persistencia y genera `docs/backlog/audit-proposals.md`. |
| `req:new` | Crea un requerimiento `REQ-DESK-*` en `docs/backlog/pending.md` (`MAJOR`, `MINOR`, `PATCH` o `--from-audit`). |
| `sync` | Sincroniza los índices `docs/backlog/index.md` y `docs/functional/index.md`; con `--export-tokens` exporta tokens W3C DTCG. |
| `check` | Valida esquemas Draft-07, frontmatter YAML, diagramas Mermaid, enlaces y fronteras (`--staged`, `--strict-tokens`, `--security`). |
| `resolve` | Cierra un `REQ-DESK-*` hacia `docs/backlog/changelog.md`, mantiene la Rolling Window y con `--bump` actualiza la versión SemVer. |

---

## 2. Ecosistemas Nativos Soportados (11)

| Identificador | Stack / Framework |
| :--- | :--- |
| `wpf` | C# / .NET WPF |
| `winui3` | C# / .NET WinUI 3 |
| `avalonia` | C# / .NET Avalonia UI |
| `maui` | C# / .NET MAUI Desktop |
| `pyside6` | Python PySide6 (Qt6) |
| `pyqt6` | Python PyQt6 |
| `flet` | Python Flet |
| `compose-desktop` | JVM Kotlin Compose Multiplatform Desktop |
| `javafx` | JVM JavaFX |
| `rust-native` | Rust Slint / Iced |
| `qt-cpp` | C++ / Qt (CMake) |

---

## 3. Contratos JSON Schema Draft-07 (9)

Todos los esquemas residen en `schemas/` y se validan sin dependencias externas:

1. `schemas/config.schema.json` — Configuración principal `.spec/config.yaml`.
2. `schemas/ecosystem-profile.schema.json` — Perfil de ecosistema nativo detectado o configurado.
3. `schemas/use-case.schema.json` — Frontmatter y estructura de casos de uso `UC-*`.
4. `schemas/user-flow.schema.json` — Frontmatter y estructura de flujos de ventana `UF-*`.
5. `schemas/requirement.schema.json` — Estructura de requerimientos `REQ-DESK-*`.
6. `schemas/design-tokens.schema.json` — Tabla de tokens de diseño y exportación W3C DTCG.
7. `schemas/local-persistence.schema.json` — Contratos de persistencia local (SQLite/WAL, migraciones, backup).
8. `schemas/distribution-release.schema.json` — Contratos de empaquetado, firma y auto-actualización.
9. `schemas/module-boundaries.schema.json` — Fronteras entre Bounded Contexts y capa de presentación.

---

## 4. Adaptadores de Harnesses (4)

`desktop-spec` distribuye reglas, comandos y skills gestionados para:

- `antigravity` — Google Antigravity (`.gemini/rules/desktop-spec.md`, `.gemini/skills/`)
- `claude` — Claude Code (`CLAUDE.md`, `.claude/commands/`, `.claude/skills/`)
- `cursor` — Cursor (`.cursor/rules/desktop-spec.mdc`, `.cursor/commands/`, `.cursor/skills/`)
- `windsurf` — Windsurf (`.windsurf/rules/desktop-spec.md`, `.windsurf/workflows/`, `.windsurf/skills/`)
