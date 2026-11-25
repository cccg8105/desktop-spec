---
artifact_type: windowing-and-os-contracts
---

# Windowing and OS Contracts

## Ventana Principal
- `MainWindow` hereda de `QMainWindow` con titulo `"Tasks Desktop Pilot"`.
- Geometria minima garantizada: `640x420` px.
- Soporte nativo para escalado HiDPI de Qt y navegacion por teclado.

## Integracion con el Sistema Operativo
- Respeta `QPalette` y esquema de color del sistema (`light`, `dark`, `system`, `high-contrast`).
- Expone `accessibleName` en controles interactivos (`title_input`, `create_button`, `task_list`) para lectores de pantalla.
