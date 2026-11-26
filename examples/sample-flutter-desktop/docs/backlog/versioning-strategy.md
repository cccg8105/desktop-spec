# Estrategia y Gobernanza de Versionamiento — sample-pyside6-desktop

> **Instruccion para el Agente de IA:**
> Clasifica toda solicitud del usuario mediante esta guía antes de abrir un requerimiento `REQ-DESK-*` en `docs/backlog/pending.md`.

---

## 1. Esquema Activo del Proyecto: `SemVer 2.0.0` (`semver`)

- **Archivo Manifiesto Sincronizado:** `pyproject.toml`
- **Version Base Detectada:** `v0.1.0`
- **Milestone Inicial en Desarrollo:** `v0.2.0`

---

## 2. Protocolo de Dos Velocidades e Impacto

### A. `MAJOR` — Cambio Incompatible (Carril Completo)
- Eliminación o cambio incompatible de fachadas públicas entre módulos (`MOD-*`), formatos de archivos de proyecto, migraciones destructivas en `SQLite (WAL)`, topología principal de ventanas (`WIN-*`) o atajos globales consolidados.
- **Ceremonia exigida:**
  1. Entrevista `/grill-me` para resolver decisiones de arquitectura, persistencia y UX.
  2. Especificación funcional según `scope` con frontera dual estricta (`UF-*` -> `UC-*` en `full-module`, `UC-*` en `domain-only`, `UF-*` en `ui-only`).
  3. Actualización de documentos técnicos impactados en `docs/technical/` y tokens en `docs/design/tokens-and-themes.md`.
  4. Pruebas *Spec-First* (`pytest`, tests de frontera modular y `pytest-qt`).
  5. Registro en `docs/backlog/pending.md` y validación del plan antes de codificar.

### B. `MINOR` — Nueva Capacidad Retrocompatible (Carril Completo)
- Nuevos flujos de ventana o diálogos (`UF-*`), nuevos casos de uso (`UC-*`), nuevos módulos `MOD-*`, nuevas tablas/columnas retrocompatibles en `SQLite (WAL)`, integraciones del SO o canales de empaquetado.
- **Ceremonia exigida:**
  1. Entrevista `/grill-me` acotada al alcance.
  2. Frontera dual funcional según `scope`:
     - `full-module`: crea/actualiza `UF-*` (interacción, FSM, accesibilidad nativa) + `UC-*` (reglas `BR-*`, OCL, persistencia local).
     - `domain-only`: crea/actualiza solo `UC-*` (`Flujos UX: N/A`).
     - `ui-only`: crea/actualiza solo `UF-*` con `invokes_use_case: N/A` (`Casos de Uso: N/A`).
     - `packaging-infra`: actualiza `docs/technical/packaging-and-release.md` / CI (`N/A` en funcionales si no cambia UX ni dominio).
  3. Registro delimitado en `docs/backlog/pending.md` y pruebas *Spec-First* previas a la implementación.

### C. `PATCH` — Correccion de Defecto o Ajuste Interno (**Carril Fast-Track / Micro-Spec**)
- Corrección de bugs puntuales, fugas de memoria o handles, condiciones de carrera en workers, bloqueo accidental del hilo UI, ajustes visuales con tokens existentes o refactorización interna sin alterar fachadas de módulo, esquema de datos ni contratos `UF-*`/`UC-*`.
- **Ceremonia reducida (*Fast-Track*):**
  1. **Omite** crear nuevos documentos `UF-*` o `UC-*` (`N/A (PATCH / Fast-Track)`, o referencia al artefacto existente si corrige una regla documentada).
  2. Registra bloque compacto `REQ-DESK-*` con tipo `Hotfix / Fix (PATCH - Fast-Track)` en `docs/backlog/pending.md` declarando exactamente los módulos y archivos afectados.
  3. Aplica protocolo `/diagnose`, escribe primero el test de regresión que reproduce el fallo y aplica el fix mínimo.

---

## 3. Reglas por Esquema Soportado (`semver` | `calver` | `sequential`)

- **`semver`:** `MAJOR.MINOR.PATCH` (ej. `1.2.0` -> `1.2.1` en `PATCH`, `1.3.0` en `MINOR`, `2.0.0` en `MAJOR`). Recomendado para aplicaciones desktop con formato de archivo versionado y *Auto-Updater*.
- **`calver`:** `YYYY.MM.MICRO` (ej. `2026.11.1`) para aplicaciones con liberaciones frecuentes por ciclo calendario.
- **`sequential`:** Incremento secuencial de versión/release (ej. `v1`, `v2` o `0.N.0` según convención del proyecto).

---

## 4. Sincronizacion Segura con el Manifiesto Nativo

1. `desktop-spec resolve <REQ-ID>` (o `dspec resolve <REQ-ID>`) archiva el requerimiento en `docs/backlog/changelog.md` sin alterar `pyproject.toml` hasta que se solicite el corte de versión.
2. `desktop-spec resolve <REQ-ID> --bump` actualiza la versión en `pyproject.toml` y `.spec/config.yaml`, **bloqueando cualquier regresión (*downgrade*)** respecto a la versión vigente del manifiesto.
