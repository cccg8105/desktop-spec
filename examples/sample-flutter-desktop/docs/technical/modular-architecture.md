---
artifact_type: modular-architecture
---

# Modular Architecture

## Estructura de Monolito Modular
- `src/modules/tasks/`: modulo de dominio y aplicacion para gestion de tareas.
  - `facade.py`: expone `TasksFacade` como unica puerta de entrada publica del modulo.
  - `create_task_use_case.py`: implementa `CreateTaskUseCase`, `CreateTaskRequest`, `CreateTaskResult` y `TaskRepository`.
  - `__init__.py`: reexporta la API publica del modulo.
- `src/ui/main_window.py`: capa de presentacion (`MainWindow`) desacoplada del almacenamiento interno, comunicandose exclusivamente mediante `TasksFacade`.

## Reglas de Frontera
- La UI no importa repositorios ni detalles internos de persistencia; solo consume `TasksFacade`.
