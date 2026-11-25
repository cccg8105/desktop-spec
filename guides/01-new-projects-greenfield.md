# Guía 01: Proyectos Nuevos (Greenfield)

Esta guía describe el ciclo completo para iniciar una aplicación de escritorio nativa desde cero con `desktop-spec` (alias `dspec`), desde la inicialización del repositorio hasta el cierre de un requerimiento con incremento SemVer.

> Hub relacionado: [README.md](../README.md) | Siguiente: [Guía 02: Proyectos Existentes (Brownfield)](02-existing-projects-brownfield.md)

---

## 1. Inicialización (`init`)

En un directorio vacío o con un *scaffold* inicial de tu ecosistema nativo (por ejemplo, `.csproj`, `pyproject.toml`, `build.gradle.kts`, `Cargo.toml` o `CMakeLists.txt`), ejecuta:

```bash
dspec init --ecosystem <perfil> --harness all --ci github
```

Si partes de una carpeta completamente vacía, omite o usa `--ecosystem` para preconfigurar el perfil y, una vez generado el manifiesto nativo, ejecuta:

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
- `docs/technical/architecture.md` y `docs/technical/tech-stack.md`: define los Bounded Contexts del monolito modular, el Event Bus en memoria y la separación UI Thread vs. Background Workers.
- `docs/design/design-tokens.md`: establece la paleta de colores, tipografía y espaciado nativos (exportables a W3C DTCG con `dspec sync --export-tokens`).

---

## 3. Creación de Requerimiento (`req:new`)

Todo cambio en el código fuente requiere un requerimiento activo en `docs/backlog/pending.md`:

```bash
dspec req:new REQ-DESK-001 --title "Configurar ventana principal y persistencia local" --type MINOR --domain core
```

Para funcionalidades nuevas (`MAJOR` o `MINOR`), documenta:
- El flujo de ventana e interacción en `docs/functional/flows/UF-CORE-001-*.md`.
- El caso de uso de dominio en `docs/functional/use-cases/UC-CORE-001-*.md`.
- La frontera unidireccional `UF -> UC` (la vista delega al caso de uso; el dominio nunca importa la vista).

---

## 4. Sincronización de Catálogos (`sync`)

Cada vez que agregues o modifiques `REQ-DESK-*`, `UF-*` o `UC-*`, actualiza los índices automáticamente:

```bash
dspec sync
```

Opcionalmente, exporta los tokens de diseño a formato W3C DTCG:

```bash
dspec sync --export-tokens
```

---

## 5. Validación de Integridad (`check`)

Antes de confirmar cambios en Git, valida contratos, frontmatter YAML, diagramas Mermaid, enlaces y fronteras de módulo:

```bash
dspec check
```

Para validar únicamente archivos en *staging* (como hace el hook `pre-commit`):

```bash
dspec check --staged
```

---

## 6. Cierre y Versionamiento (`resolve --bump`)

Cuando la implementación y las pruebas pasen, mueve el requerimiento de `pending.md` al historial inmutable `docs/backlog/changelog.md` e incrementa la versión del proyecto:

```bash
dspec resolve REQ-DESK-001 --bump
```

`resolve --bump` actualiza la versión SemVer según el tipo del requerimiento (`MAJOR`, `MINOR` o `PATCH`), mantiene la ventana deslizante (*Rolling Window*) de los últimos 5 requerimientos en `pending.md` y sincroniza los índices.
