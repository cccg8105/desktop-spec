---
description: "Onboarding Brownfield en 4 fases (.spec/bootstrap-report.md) para adoptar desktop-spec en proyectos nativos existentes."
---

# /desk-bootstrap — Adopcion Brownfield Desktop (Cursor)

Objetivo: Incorporar `desktop-spec` sobre una aplicacion de escritorio nativa existente mediante las 4 fases definidas en `.spec/skills/desktop-spec-bootstrap/SKILL.md`.

## Fases de Ejecucion

1. **Fase 1 (Diagnostico y Linea Base):**
   - Analiza el manifiesto nativo (`*.csproj`, `pyproject.toml`/`setup.cfg`, `build.gradle*`/`pom.xml`, `Cargo.toml`, `CMakeLists.txt`), toolkit UI, BD embebida y cobertura previa (`test_baseline`).
   - Actualiza `.spec/config.yaml` y `docs/technical/tech-stack.md`, e inicializa `.spec/bootstrap-report.md` como checklist GPS.
2. **Fase 2 (Extraccion As-Is — El Codigo Manda):**
   - Documenta un bloque por turno marcando `[x]` en `.spec/bootstrap-report.md` al completar: `tokens-and-themes.md`, `modular-architecture.md`, `windowing-and-os-contracts.md`, `local-persistence.md` y `packaging-and-release.md`.
3. **Fase 3 (Seleccion Full vs. Progresivo):**
   - Consulta al usuario mediante `AskQuestion` si prefiere **Modo Progresivo (Recommended)** (1-2 pares `UF-*`/`UC-*` criticos + inventario legado `Pendiente As-Is` en `docs/functional/index.md`) o **Modo Completo**.
4. **Fase 4 (Triage de Deuda sin Modificar Codigo Fuente):**
   - Registra hallazgos `[AUDIT-DESK-DOMINIO-NUM]` con evidencia `archivo:linea` en `docs/backlog/audit-proposals.md` (acoplamiento entre modulos, SQL en vistas, secretos planos, Path Traversal, bloqueo del hilo UI, fallos de accesibilidad) sin editar codigo fuente. Cierra Fase 4 en `.spec/bootstrap-report.md`.
