---
artifact_type: design-tokens
---

# Design Tokens and Themes

## Estrategia de Temas
La aplicacion soporta cuatro modos de tema resueltos mediante `QPalette` y roles semanticos del sistema operativo, sin colores hexadecimales quemados en los widgets:
- `light`: paleta clara estandar del sistema.
- `dark`: paleta oscura estandar del sistema.
- `system`: hereda automaticamente la preferencia del entorno de escritorio (`QStyleHints.colorScheme()`).
- `high-contrast`: respeta el modo de alto contraste del sistema operativo para maximizar legibilidad.

## Tokens de Color Semanticos
- `surface-window`: #FFFFFF
- `text-primary`: #111827
- `accent-primary`: #2563EB

## Densidad Desktop
- **Densidad**: `compact-desktop` (margenes de `16px`, espaciado vertical `12px`, espaciado horizontal `8px`).
- **Tamano minimo de ventana**: `640x420` px.
- **Tipografia**: fuente del sistema (`QApplication.font()`), sin tamanos fijos incompatibles con DPI scaling.
