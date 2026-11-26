# desktop-spec v0.1.0 (Estructura Base)

> **Framework y CLI de Especificación Viva para Aplicaciones de Escritorio como Monolito Modular asistidas por Agentes de IA (Spec-Driven Desktop)**

`desktop-spec` (alias `dspec`) es un framework y CLI de ingeniería gobernada por especificaciones diseñado específicamente para el desarrollo de software de escritorio (**16 ecosistemas soportados: 11 nativos base — C#/.NET WPF, WinUI 3, Avalonia, MAUI Desktop; Python PySide6/PyQt6/Flet; JVM Compose Desktop/JavaFX; Rust Slint/Iced/egui y C++/Qt —, 3 híbridos WebView con frontera IPC/FFI opcional — Tauri, Electron y Wails — y 2 nativos adicionales — Flutter Desktop y SwiftUI/AppKit macOS**) estructurado como **monolito modular standalone / local-first**.

---

## Instalación Rápida

Requiere **Python >= 3.9** (sin dependencias externas en tiempo de ejecución):

```bash
# Con uv (recomendado)
uv tool install .

# Con pipx
pipx install .
```

Verifica la instalación con:

```bash
desktop-spec --version
dspec --version
```

---

## Subcomandos del CLI (7)

| Comando | Descripción |
| :--- | :--- |
| `dspec init` | Inicializa `.spec/`, `docs/`, adaptadores de IDE/CLI y hook `pre-commit`. |
| `dspec update` | Actualiza blueprints y reglas gestionadas (`--refresh-stack`, `--dry-run`). |
| `dspec bootstrap` | Escanea un proyecto existente (Brownfield), genera `.spec/bootstrap-report.md` (checklist GPS de 4 fases), sincroniza `SYNC:TECH_STACK`/`modules:` y asegura `docs/backlog/audit-proposals.md`. |
| `dspec req:new` | Crea un requerimiento `REQ-DESK-*` autogenerado (`--impact MAJOR|MINOR|PATCH`, `--module`, `--scope` o `--from-audit AUDIT-DESK-*`). |
| `dspec sync` | Sincroniza `docs/backlog/index.md`, `docs/functional/index.md`, `docs/design/index.md` y exporta tokens con `--export-tokens`. |
| `dspec check` | Valida esquemas Draft-07, Mermaid, enlaces, Rolling Window y fronteras (`--staged`, `--strict-tokens`, `--security`). |
| `dspec resolve` | Cierra un `REQ-DESK-*` hacia `changelog.md` y con `--bump` actualiza la versión SemVer en el manifiesto y `.spec/config.yaml`. |

---

## Alcance de la Línea Base (v0.1.0 -> v1.0.0)

1. **16 Ecosistemas Soportados (*Native-First* + Híbridos WebView):** Cubre 11 frameworks nativos base de proceso único, 3 stacks híbridos WebView con contratos IPC/FFI opcionales (Tauri, Electron, Wails) y 2 ecosistemas nativos adicionales (Flutter Desktop y SwiftUI/AppKit macOS).
2. **Especialización Desktop (*Standalone / Local-First*):** Enfocado en aplicaciones de escritorio autocontenidas sin infraestructura de servidor remoto.
3. **Monolito Modular con Fronteras Estrictas:** Gobierna la separación entre módulos de dominio (Bounded Contexts, fachadas públicas, Event Bus en memoria) y la capa de presentación (MVVM/MVI, UI Thread vs. Background Workers).
4. **Doble Eje Funcional Sin Redundancia (`UF-*` vs. `UC-*`):** Mantiene separados los flujos de ventana/interacción (`UF-*`) de los casos de uso de dominio (`UC-*`) bajo una frontera explícita de delegación unidireccional.
5. **Distribución y Persistencia Local Segura:** Contempla migraciones *on-startup* con backup automático (SQLite/WAL/archivos de proyecto), credenciales en OS Keyring, empaquetado multi-SO, *Code Signing* y *Auto-Update*.

---

## Guías Operativas y Proyectos Piloto

| Recurso | Propósito |
| :--- | :--- |
| [Guía 01: Proyectos Nuevos (Greenfield)](guides/01-new-projects-greenfield.md) | Flujo `init` -> `req:new` -> `sync` -> `check` -> `resolve --bump`. |
| [Guía 02: Proyectos Existentes (Brownfield)](guides/02-existing-projects-brownfield.md) | Flujo `init` -> `bootstrap` (`.spec/bootstrap-report.md`) -> expansión Just-In-Time -> `audit-proposals.md`. |
| [Guía 03: Flujo Diario en Dos Velocidades](guides/03-daily-workflow-two-speeds.md) | Carril completo (`MAJOR`/`MINOR` con frontera `UF -> UC`) vs. Fast-Track (`PATCH` con `/diagnose`), `--staged`, `--strict-tokens` y `--security`. |
| [Guía 04: CLI, Harnesses y Contratos](guides/04-cli-harnesses-and-contracts.md) | Referencia de los 7 subcomandos, 16 ecosistemas soportados, 9 JSON Schemas Draft-07 y 4 adaptadores. |
| [Piloto .NET Desktop](examples/sample-dotnet-desktop/) | Proyecto de referencia en C# / .NET validado con `dspec check`. |
| [Piloto PySide6 Desktop](examples/sample-pyside6-desktop/) | Proyecto de referencia en Python PySide6 validado con `dspec check`. |
| [Piloto Tauri Desktop](examples/sample-tauri-desktop/) | Proyecto de referencia híbrido en Tauri (Rust + WebView) validado con `dspec check`. |
| [Piloto Flutter Desktop](examples/sample-flutter-desktop/) | Proyecto de referencia en Dart / Flutter Desktop validado con `dspec check`. |

---

## Documentación de Diseño y Planificación

| Documento | Propósito |
| :--- | :--- |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Definición de los 5 componentes principales, frontera `UC-*` / `UF-*`, taxonomía de `docs/`, perfiles soportados y límites explícitos de alcance. |
| [ROADMAP.md](ROADMAP.md) | Plan estructurado en fases iterativas y descomposición de carriles independientes. |
| [CHANGELOG.md](CHANGELOG.md) | Historial SemVer 2.0.0 del framework. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Gobernanza de ramas, `CHANGELOG.md` y uso de `scripts/bump_version.py`. |

---

## Mapa del Repositorio

```text
desktop-spec/
├── README.md                    # Portada ejecutiva del framework
├── ARCHITECTURE.md              # Componentes principales, fronteras y modelo de datos/UI
├── ROADMAP.md                   # Plan incremental por fases
├── CHANGELOG.md                 # Historial SemVer 2.0.0
├── CONTRIBUTING.md              # Flujo de ramas, changelog y versionamiento SemVer
├── pyproject.toml               # Empaquetado Hatchling (Python >=3.9, stdlib, scripts desktop-spec/dspec)
├── .gitignore                   # Exclusiones CLI Python + ecosistemas desktop
├── .gemini/rules/               # Reglas operativas del propio repositorio para agentes IA
├── .github/workflows/           # Pipelines CI y Release del framework
├── agent-prompts/               # Protocolo agnóstico AGENTS.md y prompts paso a paso
├── schemas/                     # Contratos JSON Schema Draft-07 (sin dependencias)
├── templates/                   # Activos distribuibles (.spec/, hooks pre-commit, comandos/workflows)
├── harnesses/                   # Reglas gestionadas por IDE/CLI (antigravity, claude, cursor, windsurf)
├── cli/                         # Motor CLI desktop_spec y batería de pruebas unittest
├── guides/                      # Guías operativas Hub & Spoke (Greenfield, Brownfield, Dos Velocidades, CLI)
├── examples/                    # Proyectos piloto validados con dspec check
└── scripts/                     # Utilidades de mantenimiento (ej. bump_version.py)
```
