---
description: "Ejecuta el onboarding Brownfield en 4 fases (.spec/bootstrap-report.md) para aplicaciones de escritorio nativas existentes."
---

# /desk-bootstrap — Adopcion Brownfield Desktop

Objetivo: Adoptar `desktop-spec` sobre la aplicacion de escritorio nativa existente siguiendo las 4 fases de `.spec/skills/desktop-spec-bootstrap/SKILL.md` sin perder contexto entre turnos.

## Protocolo en 4 Fases

1. **Fase 1 (Diagnostico y Linea Base):**
   - Inspecciona el manifiesto del ecosistema (`*.csproj`, `pyproject.toml`/`setup.cfg`, `build.gradle*`/`pom.xml`, `Cargo.toml`, `CMakeLists.txt`), dependencias UI, BD embebida y cobertura previa (`test_baseline`).
   - Actualiza `.spec/config.yaml` y `docs/technical/tech-stack.md`. Crea o actualiza `.spec/bootstrap-report.md` con la checklist GPS.
2. **Fase 2 (Extraccion As-Is — El Codigo Manda):**
   - Documenta un bloque por turno y marca `[x]` en `.spec/bootstrap-report.md` al completar cada uno:
     - `docs/design/tokens-and-themes.md` (paleta real, fuentes, soporte `light`/`dark`/`system`/`high-contrast` y densidad).
     - `docs/technical/modular-architecture.md` (modulos reales `MOD-*`, fachadas, acoplamientos cruzados, Event Bus y workers).
     - `docs/technical/windowing-and-os-contracts.md` (`WIN-*`, single-instance, atajos e integraciones OS) y `docs/technical/local-persistence.md` (SQLite/archivos, rutas del SO, migraciones).
     - `docs/technical/packaging-and-release.md` (instaladores nativos, firma/notarizacion y CI existente).
3. **Fase 3 (Alcance Full vs. Progresivo):**
   - Usa `AskUserQuestion` para que el usuario elija entre **Modo Progresivo (Recommended)** (documentar 1-2 pares `UF-*`/`UC-*` criticos y listar modulos legados en `docs/functional/index.md` con `Pendiente As-Is`) o **Modo Completo**.
4. **Fase 4 (Triage de Deuda sin Alterar Codigo Fuente):**
   - Registra hallazgos `[AUDIT-DESK-DOMINIO-NUM]` con evidencia `archivo:linea` en `docs/backlog/audit-proposals.md` (violaciones de frontera modular, llamadas SQL desde UI, secretos planos/Path Traversal, bloqueo del hilo UI, fallos de accesibilidad OS o falta de backup en migraciones) sin tocar codigo fuente. Marca Fase 4 completada e informa al usuario.
