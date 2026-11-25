---
artifact_type: packaging-and-release
---

# Packaging and Release

## Manifiesto y Versionado
- Definido en `pyproject.toml` con `name = "sample-pyside6-desktop"` y `version = "0.1.0"`.
- Versionado semantico sincronizado con el ciclo de release de `desktop-spec`.

## Distribucion
- Instalacion local editable mediante `pip install -e .[dev]`.
- Ejecucion de pruebas unitarias con `pytest` y verificacion documental con `dspec check --strict-tokens`.
