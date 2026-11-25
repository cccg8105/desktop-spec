---
id: UF-NOTES-001
title: Flujo de creacion de nota
invokes_use_case: UC-NOTES-001
status: Activo
module: Notes
actor: Usuario de escritorio
window_target: MainWindow
entry_trigger: Inicio de aplicacion o foco en formulario de nueva nota
accessibility:
  focus_management: Foco inicial en campo Titulo y retorno al limpiar formulario
  os_accessibility_roles: AutomationProperties.Name en controles TextBox y Button
  keyboard_navigation: Tab entre campos y Ctrl+S para guardar nota
---

# UF-NOTES-001: Flujo de creacion de nota

## 1. Maquina de Estados (FSM)
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Editing: Ingresar texto
    Editing --> Validating: Pulsar Guardar nota
    Validating --> Error: Titulo invalido [BR-01]
    Error --> Editing: Corregir titulo
    Validating --> Persisted: Nota valida
    Persisted --> Idle: Limpiar formulario
```

## 2. Matriz de Estados UI
| Estado | Boton Guardar | Campo Titulo | Mensaje de Estado |
| :--- | :--- | :--- | :--- |
| `Idle` | Habilitado | Vacio, foco inicial | Listo para crear nota |
| `Editing` | Habilitado | Con texto | Editando borrador |
| `Validating` | Deshabilitado | Solo lectura | Validando reglas |
| `Error` | Habilitado | Borde de error semantico | Titulo obligatorio |
| `Persisted` | Habilitado | Limpio | Nota guardada |

## 3. Accesibilidad y Geometria Desktop
- Ventana principal: `960x640` por defecto, minimo `640x480`.
- Navegacion por teclado: `Tab` recorre Titulo -> Contenido -> Guardar nota; `Ctrl+S` dispara el guardado.
- Contraste minimo WCAG AA en todos los temas (`light`, `dark`, `system`, `high-contrast`).
- Vista asociada: `src/Views/MainWindow.axaml`.
