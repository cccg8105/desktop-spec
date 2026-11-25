# Guía 03: Flujo Diario en Dos Velocidades

`desktop-spec` organiza el trabajo diario en dos carriles según el impacto del cambio, evitando burocracia innecesaria en correcciones menores sin sacrificar rigor en nuevas capacidades.

> Anterior: [Guía 02: Proyectos Existentes (Brownfield)](02-existing-projects-brownfield.md) | Siguiente: [Guía 04: Referencia de CLI, Harnesses y Contratos](04-cli-harnesses-and-contracts.md)

---

## 1. Carril Completo (`MAJOR` / `MINOR`)

Úsalo para nuevas funcionalidades, nuevas ventanas/flujos o cambios en contratos de dominio o persistencia local.

1. **Requerimiento:** `dspec req:new REQ-DESK-002 --title "..." --type MINOR --domain billing`
2. **Frontera `UF -> UC`:**
   - Define el flujo de ventana e interacción en `UF-*` (`docs/functional/flows/`).
   - Define la lógica de negocio en `UC-*` (`docs/functional/use-cases/`).
   - Mantén la delegación unidireccional: `UF-*` invoca a `UC-*`; `UC-*` nunca importa ni referencia componentes de UI.
3. **Sincronización y Validación:** `dspec sync && dspec check`
4. **Implementación y Cierre:** `dspec resolve REQ-DESK-002 --bump`

---

## 2. Carril Fast-Track (`PATCH`)

Úsalo para correcciones de bugs, regresiones o ajustes menores que no alteran contratos `UF-*` ni `UC-*`.

1. **Diagnóstico:** Aplica la metodología `/diagnose` (reproducir, aislar, formular hipótesis, instrumentar y prueba de regresión) antes de modificar código.
2. **Requerimiento ligero:**
   ```bash
   dspec req:new REQ-DESK-003 --title "Corregir bloqueo en hilo UI al exportar CSV" --type PATCH --domain export
   ```
   En modo `PATCH`, no se exige crear un nuevo `UC-*`.
3. **Validación y Cierre:** `dspec check --staged` y luego `dspec resolve REQ-DESK-003 --bump`.

---

## 3. Flags de Validación Especializada

Además de `dspec check`, utiliza los siguientes flags según la etapa del cambio:

| Flag | Propósito |
| :--- | :--- |
| `--staged` | Bloquea *commits fantasma* (cambios en código fuente sin `REQ-DESK-*` activo) y valida fronteras de módulo sobre los archivos en *staging* de Git. |
| `--strict-tokens` | Detecta colores hexadecimales quemados (`#RRGGBB`) en archivos de UI fuera de los archivos de tema/tokens autorizados. |
| `--security` | Ejecuta auditoría de seguridad local (por ejemplo, revisión de dependencias/configuración de secretos y superficie local). |

Ejemplo combinado antes de un release:

```bash
dspec check --strict-tokens --security
```
