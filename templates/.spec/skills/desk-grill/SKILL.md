---
name: desk-grill
description: "Entrevista tecnica estructurada de arbol de decisiones desktop nativo (frontera UF->UC, modulos MOD-*, FSM, concurrencia, persistencia local, contratos OS y seguridad) antes de especificar o codificar."
---

# desk-grill Skill

Esta skill activa el modo de entrevista arquitectonica previa para eliminar ambiguedades funcionales, modulares, de persistencia y de experiencia nativa en cualquier ecosistema de `desktop-spec` (`wpf`, `winui3`, `avalonia`, `maui-desktop`, `pyside6`, `pyqt6`, `flet`, `compose-desktop`, `javafx`, `rust-native`, `qt-cpp`, `tauri`, `electron`, `wails`, `flutter-desktop`, `swift-macos`).

## Cuando Activar esta Skill
- Invocada mediante `{{HARNESS_INTERVIEW_TRIGGER}}` al planificar requerimientos `MAJOR` o `MINOR` con decisiones abiertas en frontera `UF->UC`, modulos, estados UI, persistencia local o contratos con el sistema operativo.
- Durante el onboarding *Brownfield* (`desktop-spec-bootstrap`) para confirmar si un comportamiento legacy es intencional (*As-Is*) o deuda tecnica para `docs/backlog/audit-proposals.md`.

---

## Reglas de Oro del Entrevistador Desktop

1. **"Codigo, Modulos y Esquemas primero, humano despues":**
   Esta **estrictamente prohibido** preguntar al usuario informacion observable en manifiestos, `docs/design/tokens-and-themes.md`, `docs/technical/`, esquemas SQLite, vistas o `graphify-out/`. Inspecciona el repositorio antes de preguntar.
2. **Entrevista Concisa por Rondas:** {{HARNESS_QUESTION_STRATEGY}}. Formula de 2 a 4 decisiones concretas ordenadas con la opcion recomendada primero y trade-offs claros.
3. **Arbol de Decision Quirurgico Desktop:**
   Enfoca tus preguntas exclusivamente en decisiones que impactan los artefactos de `desktop-spec`:
   - **Frontera Funcional `UF-*` vs `UC-*` (`functional-boundary-guidelines.md`):** El cambio requiere flujo dual `UF -> UC` (`full-module`), solo dominio/worker (`domain-only`), o solo ergonomia/presentacion (`ui-only`)? Que reglas `[BR-XX]` o invariantes OCL aplican?
   - **FSM, Concurrencia e Invariantes UI (`ui-contracts-guidelines.md`):** Como se evita el doble envio (`NoDoubleSubmit`)? El borrador se conserva ante fallo de dominio (`PreserveDraftOnError`)? Que operaciones pasan a background worker con cancelacion (`NoMainThreadBlock`)? Se exige confirmacion de cambios sin guardar al cerrar ventana (`GuardUnsavedChangesOnClose`)?
   - **Monolito Modular (`modular-architecture.md`):** Que modulo `MOD-*` es dueno de los datos y cual es su fachada publica? La comunicacion con otros modulos es sincrona por puerto o asincrona por Event Bus interno?
   - **Ventanas, SO y Persistencia (`windowing-and-os-contracts.md`, `local-persistence.md`):** Se abre en ventana modal, panel acoplado o ventana secundaria `WIN-*`? Que atajos multiplataforma (`Ctrl` vs `Cmd`) y roles de accesibilidad OS aplican? Requiere migracion SQLite con backup on-startup o resguardo de credenciales en OS Keyring?
   - **Frontera IPC / FFI (Opcional — Shell Hibrido WebView):** Cuando el proyecto usa `tauri`, `electron` o `wails`, que comandos/canales IPC (`invoke`, `ipcMain`/`ipcRenderer`, bindings Go) se exponen al WebView, como se validan payloads y permisos, y que limites de aislamiento (`contextIsolation`, preload, allowlist) protegen la frontera hacia el nucleo nativo?
   - **Brownfield As-Is vs. Bug:** *"En `MainViewModel.cs:112` la consulta SQLite corre en el hilo UI: es comportamiento heredado a migrar ahora o deuda para `audit-proposals.md`?"*

---

## Protocolo de Cierre
Al despejar las decisiones abiertas:
1. Resume brevemente los acuerdos alcanzados (alcance `UF->UC`, modulos `MOD-*`, FSM, concurrencia, persistencia y contratos OS).
2. Formaliza los artefactos afectados (`UC-*`, `UF-*`, `tokens-and-themes.md`, `modular-architecture.md`, `windowing-and-os-contracts.md`, `local-persistence.md`, `tech-stack.md`, `packaging-and-release.md`) y registra el `REQ-DESK-*` en `docs/backlog/pending.md` (o `AUDIT-DESK-*` si es triage Brownfield).
