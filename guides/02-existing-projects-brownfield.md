# Guía 02: Proyectos Existentes (Brownfield)

Esta guía explica cómo adoptar `desktop-spec` en una aplicación de escritorio nativa ya existente sin detener el desarrollo ni reescribir el código legado de golpe.

> Anterior: [Guía 01: Proyectos Nuevos (Greenfield)](01-new-projects-greenfield.md) | Siguiente: [Guía 03: Flujo Diario en Dos Velocidades](03-daily-workflow-two-speeds.md)

---

## 1. Inicialización Segura (`init`)

En la raíz del repositorio existente, ejecuta:

```bash
dspec init
```

`desktop-spec` detecta automáticamente el ecosistema nativo (`.csproj`, `pyproject.toml`, `Cargo.toml`, `CMakeLists.txt`, `build.gradle.kts`, `pom.xml`) y preserva tu código fuente, reglas personalizadas y hooks previos (inyectando el bloque gestionado sin destruir contenido propio).

---

## 2. Inventario Automático (`bootstrap`)

Ejecuta el escaneo inicial para levantar el mapa *As-Is* del proyecto:

```bash
dspec bootstrap
```

Este comando analiza el repositorio y genera o actualiza:
- Inventario de módulos/dominios detectados y estado de graduación en `docs/functional/index.md`.
- Catálogo de ventanas/pantallas y persistencia local detectada.
- `docs/backlog/audit-proposals.md`: lista priorizada de propuestas técnicas y de deuda arquitectónica detectadas.

---

## 3. Expansión Just-In-Time (JIT)

No intentes documentar toda la aplicación heredada el primer día. Aplica expansión *Just-In-Time*:

1. Cuando vayas a tocar un módulo legado, documenta primero su flujo `UF-*` y caso de uso `UC-*` *As-Is* en `docs/functional/`.
2. Al crear el `UC-*` del dominio, `desktop-spec` gradúa progresivamente ese dominio en `docs/functional/index.md`.
3. Ejecuta `dspec sync` y `dspec check` para asegurar que los nuevos contratos cumplan los esquemas Draft-07.

---

## 4. Promoción desde `audit-proposals.md`

Las mejoras identificadas durante `bootstrap` quedan registradas en `docs/backlog/audit-proposals.md` con su identificador de propuesta (por ejemplo, `PROP-001`). Para convertir una propuesta en un requerimiento activo:

```bash
dspec req:new REQ-DESK-010 --from-audit PROP-001 --type MINOR --domain core
```

Esto vincula la trazabilidad entre la auditoría inicial y el requerimiento en `docs/backlog/pending.md`, permitiendo cerrarlo posteriormente con `dspec resolve REQ-DESK-010 --bump`.
