# Guía de Contribución y Gobernanza del Repositorio — desktop-spec

Este documento define el flujo de ramas, registro de cambios y versionamiento SemVer para el desarrollo de `desktop-spec` (equivalente al modelo usado en `backend-spec` y `frontend-spec`).

---

## 1. Flujo de Ramas (Una Rama por Bloque de Cambios)

- **`main` es la rama protegida de integración:** no se realizan desarrollos directos sobre `main`.
- Para cada oleada, funcionalidad, corrección o bloque documental, crea una rama nueva desde `main`:
  - `feat/<bloque>` (ej. `feat/wave-1-structure-and-contracts`, `feat/wave-2-templates-core`)
  - `fix/<correccion>` (ej. `fix/windowing-schema-regex`)
  - `chore/<mantenimiento>` (ej. `chore/ci-release-pipeline`)
- Utiliza mensajes de commit descriptivos bajo *Conventional Commits* (`feat(...)`, `fix(...)`, `chore(...)`, `docs(...)`).

---

## 2. Registro de Cambios (`CHANGELOG.md`)

- Basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
- Todo PR o rama debe actualizar la sección `## [Unreleased]` de [CHANGELOG.md](CHANGELOG.md) agrupando los cambios en `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed` o `Security`.
- Antes de etiquetar un release `vX.Y.Z`, los cambios pasan a `## [X.Y.Z] - YYYY-MM-DD`.

---

## 3. Versionamiento SemVer 2.0.0 (`scripts/bump_version.py`)

El proyecto sigue [Semantic Versioning 2.0.0](https://semver.org/lang/es/):

- **`MAJOR` (`X.0.0`):** Cambios incompatibles en `.spec/`, `docs/`, campos obligatorios de `schemas/` o contratos públicos del CLI `desktop-spec` / `dspec`.
- **`MINOR` (`0.X.0`):** Nuevos ecosistemas nativos, blueprints, comandos o validaciones compatibles hacia atrás.
- **`PATCH` (`0.0.X`):** Correcciones de bugs, validaciones y mejoras documentales compatibles hacia atrás.

### Comandos del Script de Versionamiento

```bash
# Verificar coherencia de versión en todos los archivos versionados
python scripts/bump_version.py --check

# Simular actualización atómica sin escribir archivos
python scripts/bump_version.py 0.2.0 --dry-run

# Aplicar bump atómico (y opcionalmente crear commit + tag anotado tras pruebas)
python scripts/bump_version.py 0.2.0
python scripts/bump_version.py 0.2.0 --tag
```
