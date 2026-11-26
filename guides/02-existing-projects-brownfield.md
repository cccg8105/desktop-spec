# Guía 02: Proyectos Existentes (Brownfield)

Esta guía explica cómo adoptar `desktop-spec` en una aplicación de escritorio ya existente sin detener el desarrollo ni reescribir el código legado de golpe.

> Anterior: [Guía 01: Proyectos Nuevos (Greenfield)](01-new-projects-greenfield.md) | Siguiente: [Guía 03: Flujo Diario en Dos Velocidades](03-daily-workflow-two-speeds.md)

---

## 1. Inicialización Segura (`init`)

En la raíz del repositorio existente, ejecuta:

```bash
dspec init
```

`desktop-spec` detecta automáticamente el ecosistema entre los 16 perfiles soportados a partir de su manifiesto (`.csproj`, `pyproject.toml`, `Cargo.toml`, `CMakeLists.txt`, `build.gradle.kts`, `pom.xml`, `src-tauri/Cargo.toml`, `package.json`, `wails.json`, `pubspec.yaml`, `Package.swift`) y preserva tu código fuente, reglas personalizadas y hooks previos (inyectando el bloque gestionado sin destruir contenido propio).

---

## 2. Inventario Automático (`bootstrap`)

Ejecuta el escaneo inicial para levantar el mapa *As-Is* del proyecto:

```bash
dspec bootstrap
```

Este comando analiza el repositorio y realiza las siguientes acciones:
- Genera `.spec/bootstrap-report.md`: reporte técnico y **checklist GPS de 4 fases** (Línea Base/Manifiesto, Arquitectura/Ventanas/Persistencia, Flujos UX/Casos de Uso, y Triage de Deuda) que preserva tus casillas marcadas `[x]` en ejecuciones posteriores. Usa `dspec bootstrap --reset` si necesitas reiniciar las casillas, o `--mode full|progressive` para ajustar el alcance.
- Actualiza el bloque gestionado `SYNC:TECH_STACK` en `docs/technical/tech-stack.md` y la clave `modules:` en `.spec/config.yaml`.
- Alimenta la sección `PENDING_MODULES` en `docs/functional/index.md` con los módulos candidatos detectados.
- Asegura la plantilla `docs/backlog/audit-proposals.md`, donde el agente registra los hallazgos de deuda técnica, fugas de frontera o riesgos locales bajo el formato `[AUDIT-DESK-<DOMINIO>-<NUM>]`.

---

## 3. Expansión Just-In-Time (JIT)

No intentes documentar toda la aplicación heredada el primer día. Aplica expansión *Just-In-Time*:

1. Cuando vayas a tocar un módulo legado, documenta primero su flujo `UF-*` (`docs/functional/user-flows/`) y caso de uso `UC-*` (`docs/functional/use-cases/`) *As-Is*.
2. Al crear el `UC-*` del dominio, `desktop-spec` gradúa progresivamente ese dominio y lo retira de `PENDING_MODULES` en `docs/functional/index.md`.
3. Ejecuta `dspec sync` y `dspec check` para asegurar que los nuevos contratos cumplan los esquemas Draft-07.

---

## 4. Promoción desde `audit-proposals.md`

Los hallazgos registrados por el agente en `docs/backlog/audit-proposals.md` llevan un identificador de auditoría con el formato `AUDIT-DESK-<DOMINIO>-<NUM>` (por ejemplo, `AUDIT-DESK-CORE-001`). Para promover un hallazgo a un requerimiento activo en `docs/backlog/pending.md`:

```bash
dspec req:new --from-audit AUDIT-DESK-CORE-001
```

Esto autogenera el requerimiento `REQ-DESK-*` correspondiente con la trazabilidad vinculada a la auditoría inicial, permitiendo cerrarlo posteriormente con `dspec resolve REQ-DESK-CORE-001 --bump`.
