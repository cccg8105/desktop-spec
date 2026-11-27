# Guía 01: Proyectos Nuevos (Greenfield)

Esta guía describe el ciclo completo para iniciar una aplicación de escritorio desde cero con `desktop-spec` (alias `dspec`), desde la inicialización del repositorio hasta el cierre de un requerimiento con incremento SemVer.

> Hub relacionado: [README.md](../README.md) | Siguiente: [Guía 02: Proyectos Existentes (Brownfield)](02-existing-projects-brownfield.md)

---

## 1. Inicialización (`init`)

En un directorio vacío o con un *scaffold* inicial de tu ecosistema desktop (por ejemplo, `.csproj`, `pyproject.toml`, `build.gradle.kts`, `Cargo.toml`, `CMakeLists.txt`, `src-tauri/Cargo.toml`, `package.json`, `wails.json`, `pubspec.yaml` o `Package.swift`), ejecuta:

```bash
dspec init --ecosystem <perfil> --harness all --ci github
```

Si partes de una carpeta completamente vacía, usa `--ecosystem` para preconfigurar el perfil objetivo y, una vez generado el manifiesto real, ejecuta:

```bash
dspec update --refresh-stack
```

Esto crea:
- `.spec/config.yaml` y `.spec/templates/` (blueprints internos).
- `docs/functional/`, `docs/design/`, `docs/technical/` y `docs/backlog/`.
- Adaptadores para los harnesses seleccionados (`antigravity`, `claude`, `cursor`, `windsurf`) y el hook `.git/hooks/pre-commit`.

---

## 2. Ceremonia de Fundación (Día 0)

Antes de escribir lógica de negocio, completa los documentos base en `docs/`:
- **Los 5 pilares técnicos (`docs/technical/`):**
  - `docs/technical/tech-stack.md`: runtime, lenguaje, toolkit UI, persistencia local y runners de prueba.
  - `docs/technical/modular-architecture.md`: Bounded Contexts (`MOD-*`) del monolito modular, fachadas públicas, Event Bus en memoria y separación UI Thread vs. Background Workers.
  - `docs/technical/windowing-and-os-contracts.md`: ventanas (`WIN-*`), ciclo de vida, bandeja del sistema, atajos globales y OS Keyring.
  - `docs/technical/local-persistence.md`: motor embebido (ej. SQLite WAL), migraciones *on-startup* y respaldos automáticos.
  - `docs/technical/packaging-and-release.md`: instaladores multi-SO, *Code Signing* y canal de *Auto-Update*.
- **Diseño y temas (`docs/design/`):**
  - `docs/design/tokens-and-themes.md`: establece la paleta de colores, tipografía, densidad y temas (`light`/`dark`/`system`/`high-contrast`), exportables a formato W3C DTCG con `dspec sync --export-tokens`.

---

## 3. Creación de Requerimiento (`req:new`)

Todo cambio en el código fuente requiere un requerimiento activo en `docs/backlog/pending.md`. El identificador (`REQ-DESK-CORE-001`) se autogenera a partir del módulo indicado:

```bash
dspec req:new "Configurar ventana principal y persistencia local" --impact MINOR --module core --scope full-module
```

Para funcionalidades nuevas (`MAJOR` o `MINOR`), documenta:
- El flujo de ventana e interacción en `docs/functional/user-flows/UF-CORE-001-*.md`.
- El caso de uso de dominio en `docs/functional/use-cases/UC-CORE-001-*.md`.
- La frontera unidireccional `UF -> UC` (la vista delega al caso de uso; el dominio nunca importa la vista).

---

## 4. Sincronización de Catálogos (`sync`)

Cada vez que agregues o modifiques `REQ-DESK-*`, `UF-*`, `UC-*` o tokens de diseño, actualiza los índices automáticamente (`docs/backlog/index.md`, `docs/functional/index.md` y `docs/design/index.md`):

```bash
dspec sync
```

Opcionalmente, exporta `docs/design/tokens-and-themes.md` a `.spec/specs/design.tokens.json` en formato W3C DTCG:

```bash
dspec sync --export-tokens
```

---

## 5. Validación de Integridad (`check`)

Antes de confirmar cambios en Git, valida enlaces, esquemas JSON Draft-07, diagramas Mermaid, Rolling Window y fronteras de módulo:

```bash
dspec check
```

Para validar únicamente archivos en *staging* (como hace el hook `pre-commit`):

```bash
dspec check --staged
```

---

## 6. Cierre y Versionamiento (`resolve --bump`)

Cuando la implementación y las pruebas pasen, cierra el requerimiento activo:

```bash
dspec resolve REQ-DESK-CORE-001 --bump
```

`resolve --bump` realiza las siguientes operaciones:
- Retira el requerimiento de `docs/backlog/pending.md`.
- Lo archiva con fecha de resolución en el historial inmutable `docs/backlog/changelog.md`.
- Sincroniza los índices documentales (`docs/backlog/index.md`, `docs/functional/index.md` y `docs/design/index.md`).
- Con `--bump`, actualiza la versión en el manifiesto del ecosistema y en `.spec/config.yaml` con protección anti-downgrade (puedes usar `--force-version` únicamente si necesitas forzar una versión inferior).

> Nota sobre la **Rolling Window (`<= 3` filas)**: esta regla aplica a la tabla `## Historial de Revisiones` de los documentos técnicos y funcionales (no limita la cantidad de requerimientos en `pending.md`) y se valida automáticamente en `dspec check`.
