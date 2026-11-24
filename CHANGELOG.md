# Registro de Cambios (Changelog)

Todos los cambios notables en `desktop-spec` se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y este proyecto se adhiere a [Semantic Versioning 2.0.0](https://semver.org/lang/es/).

---

## Guía de Versionamiento Semántico (SemVer)

- **MAJOR (x.0.0):** Cambios que rompen la compatibilidad hacia atrás en estructura (`.spec/`, `docs/`), campos obligatorios de `schemas/` o contratos públicos del CLI (`desktop-spec` / `dspec`).
- **MINOR (0.x.0):** Nuevas capacidades compatibles hacia atrás (nuevos perfiles de ecosistema desktop, nuevos blueprints, comandos o validaciones opcionales).
- **PATCH (0.0.x):** Correcciones y mejoras internas compatibles hacia atrás.

---

## [Unreleased]

### Added
- Estructura inicial del repositorio (`cli/`, `schemas/`, `templates/`, `harnesses/`, `agent-prompts/`, `guides/`, `examples/`, `scripts/`).
- Definición de arquitectura base en `ARCHITECTURE.md` (enfoque *native-first* para monolitos modulares y frontera estricta entre `UC-*` y `UF-*`).
- Plan iterativo en fases y estrategia de ejecución paralela multi-agente (`/teamwork`) en `ROADMAP.md`.
- Contratos formales de Fase 1 (`Wave 1`): 9 esquemas JSON Schema Draft-07 sin dependencias externas (`requirement`, `use-case`, `user-flow`, `design/tokens-and-themes`, `technical/{tech-stack,modular-architecture,windowing-and-os-contracts,local-persistence,packaging-and-release}`), plantilla `templates/.spec/config.yaml` y 4 guías normativas (`functional-boundary-guidelines.md`, `ocl-guidelines.md`, `ui-contracts-guidelines.md`, `design-guidelines.md`).
- Gobernanza propia del repositorio: regla de rama nueva por bloque de cambios en `.gemini/rules/repo-workflow.md` y `CONTRIBUTING.md`, junto con validador/actualizador atómico SemVer en `scripts/bump_version.py`.

---

## [0.1.0] - Planned

### Planned
- Fase 1: JSON Schemas Draft-07, `.spec/config.yaml` y guías normativas base.
- Fase 2: Blueprints en `templates/`, `agent-prompts/` y adaptadores `harnesses/`.
- Fase 3: Motor CLI `desktop-spec` / `dspec` en biblioteca estándar Python.
- Fase 4: Proyectos piloto nativos, guías operativas en `guides/` y pipelines CI/Release.
