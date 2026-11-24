---
description: "Adopcion Brownfield en 4 fases (.spec/bootstrap-report.md) para aplicaciones de escritorio nativas existentes."
---

# /desk-bootstrap — Adopcion Brownfield Desktop (Windsurf)

1. **Fase 1 (Diagnostico y Linea Base):**
   - Inspecciona el manifiesto nativo (`*.csproj`, `pyproject.toml`/`setup.cfg`, `build.gradle*`/`pom.xml`, `Cargo.toml`, `CMakeLists.txt`), toolkit UI, BD embebida y cobertura de tests (`test_baseline`).
   - Actualiza `.spec/config.yaml` y `docs/technical/tech-stack.md`; crea `.spec/bootstrap-report.md`.
2. **Fase 2 (Extraccion As-Is por Bloques):**
   - Documenta un bloque por turno marcando `[x]` en `.spec/bootstrap-report.md` al terminar cada uno: `tokens-and-themes.md`, `modular-architecture.md`, `windowing-and-os-contracts.md`, `local-persistence.md` y `packaging-and-release.md`.
3. **Fase 3 (Alcance Full vs. Progresivo):**
   - Detente con opciones `A) Modo Progresivo (Recomendado)` vs `B) Modo Completo` para que el usuario decida cuantos pares `UF-*`/`UC-*` documentar inicialmente frente a `Modulos Legados Detectados`.
4. **Fase 4 (Triage de Deuda y Cierre):**
   - Registra hallazgos `[AUDIT-DESK-DOMINIO-NUM]` con evidencia `archivo:linea` en `docs/backlog/audit-proposals.md` sin editar codigo fuente, marca completada la Fase 4 y reporta el resultado.
