---
artifact_type: local-persistence
---

# Local Persistence

## Estrategia Actual
- El piloto utiliza `InMemoryTaskRepository` implementando el protocolo `TaskRepository` en `src/modules/tasks/create_task_use_case.py`.
- Permite validar `UC-TASKS-001` de extremo a extremo sin dependencias externas de base de datos.

## Evolucion Planificada
- Sustituir `InMemoryTaskRepository` por un adaptador SQLite local en `QStandardPaths.AppDataLocation` manteniendo intacto el contrato `TaskRepository`.
