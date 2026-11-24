# Comando: 02b_plan_modular_architecture

> **Proposito:** Disenar o actualizar la arquitectura del monolito modular nativo, fronteras de modulos `MOD-*`, Event Bus en memoria y modelo de concurrencia (Etapa 2B).

## Instrucciones para el Agente:
1. Abre `docs/technical/modular-architecture.md` y consulta `.spec/templates/_template_modular_architecture.md`.
2. Registra o actualiza los modulos de dominio afectados (`MOD-[DOMINIO]-[NUM]`) verificando:
   - Responsabilidad acotada y **fachada/puerto publico** unico por modulo.
   - Alcance exclusivo de persistencia (`owned_persistence_scope`), prohibiendo que la capa UI o un modulo ajeno acceda directamente a tablas/repositorios internos de otro modulo.
   - Reglas de dependencia aciclica (`acyclic_modules: true`, `forbid_cross_module_internals: true`, `forbid_ui_direct_persistence: true`) y herramienta de verificacion arquitectonica (`NetArchTest`, `import-linter`, `ArchUnit`, checks de crates/modulos).
3. Actualiza los diagramas Mermaid (`classDiagram` de modulos y fachadas, y `sequenceDiagram` entre UI Thread, ViewModel/Presenter, Fachada de Modulo, Event Bus y Background Workers).
4. Especifica eventos publicados/suscritos en el **Event Bus interno en memoria** (`internal_event_bus`) y el modelo de concurrencia **UI Thread vs. Background Workers** con soporte de cancelacion (`CancellationToken` / corrutinas / `QThread` / `tokio`).
5. Actualiza `## Historial de Revisiones (Ultimos Cambios)` manteniendo un maximo de 3 filas y valida con `dspec check`.
