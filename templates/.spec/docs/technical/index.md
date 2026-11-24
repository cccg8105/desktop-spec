# Indice de Documentacion Tecnica Desktop — {{PROJECT_NAME}}

> **Instruccion para el Agente de IA:**
> Utiliza este indice O(1) para cargar **unicamente** el documento tecnico relevante para tu tarea actual:
> - ¿Ecosistema (`{{RUNTIME_LABEL}}`), toolkit UI (`{{UI_TOOLKIT}}`), presupuestos desktop (`cold_startup_ms`, `idle_ram_mb`, `ui_frame_budget_ms`, `installer_max_mb`) o seguridad local? -> [`tech-stack.md`](./tech-stack.md)
> - ¿Modulos de dominio (`MOD-*`), fachadas publicas, reglas aciclicas, Event Bus en memoria o concurrencia UI Thread vs. Background Workers? -> [`modular-architecture.md`](./modular-architecture.md)
> - ¿Topologia de ventanas (`WIN-*`), Single-Instance Lock, atajos `Ctrl`/`Cmd`, guardia de cierre o integraciones del SO? -> [`windowing-and-os-contracts.md`](./windowing-and-os-contracts.md)
> - ¿Base de datos embebida (`{{EMBEDDED_DB}}`), rutas estándar del SO, formatos de proyecto o migraciones *on-startup* con respaldo previo? -> [`local-persistence.md`](./local-persistence.md)
> - ¿CI multi-SO (`windows-latest`, `macos-latest`, `ubuntu-latest`), instaladores nativos, Code Signing/Notarization o Auto-Updater? -> [`packaging-and-release.md`](./packaging-and-release.md)
> - Blueprints de referencia tecnica: [`.spec/templates/`](../../.spec/templates/)

---

## Artefactos Tecnicos del Monolito Modular

| Artefacto | Archivo | Responsabilidad Clave |
| :--- | :--- | :--- |
| **Stack y Politicas Locales** | [tech-stack.md](./tech-stack.md) | Ecosistema (`{{RUNTIME_LABEL}}`), toolkit UI (`{{UI_TOOLKIT}}`), DB embebida (`{{EMBEDDED_DB}}`), presupuestos desktop y seguridad local. |
| **Arquitectura Modular** | [modular-architecture.md](./modular-architecture.md) | Módulos `MOD-*`, fachadas públicas, dependencias acíclicas, Event Bus en memoria y concurrencia UI/Workers. |
| **Ventanas y Contratos SO** | [windowing-and-os-contracts.md](./windowing-and-os-contracts.md) | Topología `WIN-*`, *Single-Instance Lock*, atajos de teclado, guardia de cierre e integraciones nativas del SO. |
| **Persistencia Local** | [local-persistence.md](./local-persistence.md) | Diagrama `erDiagram`, tablas embebidas, rutas del SO, archivos de proyecto y migraciones *on-startup*. |
| **Empaquetado y Release** | [packaging-and-release.md](./packaging-and-release.md) | Matriz CI multi-SO, instaladores nativos, firma/notarización, *Auto-Updater* y variables de build. |

---

## Principios Tecnicos Invariables

1. **Monolito Modular Standalone:** La aplicación se ejecuta como un proceso nativo autocontenido sin servidor externo propio. La presentación (`{{UI_DIR}}`) interactúa únicamente con las fachadas públicas de los módulos (`{{MODULES_DIR}}`).
2. **Fronteras Verificables:** Prohibido que la capa UI acceda directamente a SQL/repositorios de persistencia y prohibido que un módulo importe internos privados de otro módulo.
3. **Hilo UI No Bloqueante:** Toda operación de E/S en disco, consultas pesadas en `{{EMBEDDED_DB}}` o procesamiento intensivo se ejecuta fuera del hilo principal de UI con soporte de cancelación.
4. **Sincronia Viva:** Todo cambio en módulos actualiza `modular-architecture.md`; todo cambio en ventanas o atajos actualiza `windowing-and-os-contracts.md`; todo cambio de tablas o formatos de archivo actualiza `local-persistence.md`.
