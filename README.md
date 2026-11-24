# desktop-spec v0.1.0 (Estructura Base)

> **Framework y CLI de Especificación Viva para Aplicaciones de Escritorio Nativas como Monolito Modular asistidas por Agentes de IA (Spec-Driven Desktop)**

`desktop-spec` adapta los principios de ingeniería gobernada por especificaciones de `backend-spec` y `frontend-spec` a las particularidades del software de escritorio nativo (**C#/.NET WPF, WinUI 3, Avalonia, MAUI Desktop; Python PySide6/PyQt6/Flet; JVM Compose Desktop/JavaFX; Rust Slint/Iced y C++/Qt**) estructurado como **monolito modular standalone / local-first**.

---

## Alcance de la Línea Base (v0.1.0 -> v1.0.0)

1. **Prioridad Nativa (*Native-First*):** Los perfiles iniciales cubren frameworks nativos de proceso único. Shells híbridos con WebView (Electron, Tauri, Wails) quedan planificados para una extensión posterior (`v1.1+`).
2. **Especialización Desktop (*Standalone / Local-First*):** No incluye infraestructura de servidor remoto ni contratos HTTP de backend propio; ese alcance corresponde a un futuro framework full-stack.
3. **Monolito Modular con Fronteras Estrictas:** Gobierna la separación entre módulos de dominio (Bounded Contexts, fachadas públicas, Event Bus en memoria) y la capa de presentación (MVVM/MVI, UI Thread vs. Background Workers).
4. **Doble Eje Funcional Sin Redundancia (`UF-*` vs. `UC-*`):** Mantiene separados los flujos de ventana/interacción (`UF-*`) de los casos de uso de dominio (`UC-*`) bajo una frontera explícita de delegación unidireccional.
5. **Distribución y Persistencia Local Segura:** Contempla migraciones *on-startup* con backup automático (SQLite/WAL/archivos de proyecto), credenciales en OS Keyring, empaquetado multi-SO, *Code Signing* y *Auto-Update*.

---

## Documentación de Diseño y Planificación

| Documento | Propósito |
| :--- | :--- |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Definición de los 5 componentes principales, frontera `UC-*` / `UF-*`, taxonomía de `docs/`, perfiles nativos y qué aplica o se excluye frente a backend/frontend web. |
| [ROADMAP.md](ROADMAP.md) | Plan estructurado en fases iterativas (Fases 0 a 5) y descomposición de carriles independientes para ejecución paralela con `/teamwork`. |
| [CHANGELOG.md](CHANGELOG.md) | Historial SemVer 2.0.0 del framework. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Gobernanza de ramas por bloque de cambios, `CHANGELOG.md` y uso de `scripts/bump_version.py`. |

---

## Mapa del Repositorio

```text
desktop-spec/
├── README.md                    # Portada ejecutiva del framework
├── ARCHITECTURE.md              # Componentes principales, fronteras y modelo de datos/UI
├── ROADMAP.md                   # Plan incremental por fases y matriz /teamwork
├── CHANGELOG.md                 # Historial SemVer 2.0.0
├── CONTRIBUTING.md              # Flujo de ramas, changelog y versionamiento SemVer
├── pyproject.toml               # Empaquetado Hatchling (Python >=3.9, stdlib, scripts desktop-spec/dspec)
├── .gitignore                   # Exclusiones CLI Python + ecosistemas desktop nativos
├── .gemini/rules/               # Reglas operativas del propio repositorio para agentes IA
├── .github/workflows/           # Pipelines CI y Release del framework
├── agent-prompts/               # Protocolo agnóstico AGENTS.md y prompts paso a paso
├── schemas/                     # Contratos JSON Schema Draft-07 (sin dependencias)
├── templates/                   # Activos distribuibles (.spec/, hooks pre-commit, comandos/workflows)
├── harnesses/                   # Reglas gestionadas por IDE/CLI (antigravity, claude, cursor, windsurf)
├── cli/                         # Motor CLI desktop_spec y batería de pruebas unittest
├── guides/                      # Guías operativas Hub & Spoke (Greenfield, Brownfield, Dos Velocidades, CLI)
├── examples/                    # Proyectos piloto nativos validados con dspec check
└── scripts/                     # Utilidades de mantenimiento (ej. bump_version.py)
```
