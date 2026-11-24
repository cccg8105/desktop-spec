---
trigger: always_on
description: "Reglas de gobernanza del propio repositorio desktop-spec: rama nueva por bloque de cambios, CHANGELOG.md, versionamiento SemVer y validacion previa al commit."
---

# Reglas Operativas del Repositorio — desktop-spec

Estas reglas aplican a cualquier agente de IA o colaborador que modifique el repositorio del framework `desktop-spec`:

1. **Rama Nueva Obligatoria por Bloque de Cambios:**
   - **Prohibido** commitear bloques nuevos de trabajo directamente sobre `main`.
   - Antes de iniciar una oleada, funcionalidad, corrección o cambio estructural, crea una rama nueva descriptiva desde `main` (por ejemplo: `feat/wave-2-templates-and-cli`, `fix/schema-validator-edge-case`, `chore/repo-governance`).
   - Mantén cada rama acotada a un bloque coherente de cambios listo para revisión o merge hacia `main`.

2. **Actualización Obligatoria de `CHANGELOG.md`:**
   - Todo bloque de cambios debe registrar sus modificaciones bajo `## [Unreleased]` en `CHANGELOG.md` siguiendo *Keep a Changelog* (`Added`, `Changed`, `Fixed`, `Removed`).
   - Al realizar un corte de versión (`vX.Y.Z`), mueve los elementos de `## [Unreleased]` a `## [X.Y.Z] - YYYY-MM-DD`.

3. **Versionamiento SemVer 2.0.0 (`scripts/bump_version.py`):**
   - El framework se adhiere estrictamente a **Semantic Versioning 2.0.0** (`MAJOR.MINOR.PATCH` y pre-releases `-alpha.N`, `-beta.N`, `-rc.N`).
   - Antes de confirmar cambios o hacer merge a `main`, ejecuta:
     ```bash
     python scripts/bump_version.py --check
     ```
   - Para subir la versión de forma atómica en todos los archivos versionados del repositorio, utiliza `python scripts/bump_version.py <X.Y.Z>` (nunca edites versiones manualmente en un solo archivo).

4. **Integridad, Estilo y Fronteras:**
   - No utilices emojis en archivos del repositorio ni en mensajes de commit.
   - Respeta el orden de oleadas de `ROADMAP.md` y la frontera `UF-*` / `UC-*` definida en `ARCHITECTURE.md`.
