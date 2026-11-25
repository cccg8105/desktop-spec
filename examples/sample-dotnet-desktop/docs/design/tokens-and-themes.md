---
artifact_type: design-tokens
theme_modes:
  - light
  - dark
  - system
  - high-contrast
density_modes:
  - compact
  - standard
  - comfortable
window_chrome:
  titlebar_style: native
  backdrop_material: solid-surface
  titlebar_height_px: 36
  corner_style: os-default
---

# Sistema de Tokens y Temas Nativos — sample-dotnet-desktop

> **Catalogo canonico de tokens semanticos de sample-dotnet-desktop (v0.1.0).**
> Rige la apariencia nativa multi-tema (`light`, `dark`, `system`, `high-contrast`), la densidad de herramienta operativa y la traduccion a recursos nativos del toolkit definido en [`docs/technical/tech-stack.md`](../technical/tech-stack.md).

---

## 1. Colores Semanticos

| Token | Modo Claro | Modo Oscuro | Alto Contraste | Rol de Uso |
| :--- | :--- | :--- | :--- | :--- |
| `bg-base` | `#F5F6F8` | `#111317` | `#000000` | Fondo base de la ventana principal y contenedores raiz |
| `surface` | `#FFFFFF` | `#1A1D23` | `#000000` | Paneles laterales, inspectores, barras y formularios |
| `surface-elevated` | `#F0F2F5` | `#232730` | `#1A1A1A` | Menus contextuales, popovers, dialogos y cabeceras de tabla |
| `primary` | `#0F52BA` | `#4C8DFF` | `#FFFF00` | Accion primaria, seleccion activa e indicador de foco |
| `primary-hover` | `#0B3E91` | `#70A5FF` | `#FFFFFF` | Estado hover o presionado sobre accion primaria |
| `text-main` | `#181B20` | `#F1F3F5` | `#FFFFFF` | Texto operativo principal y encabezados (>= 7:1) |
| `text-muted` | `#4E5866` | `#9AA4B2` | `#E0E0E0` | Etiquetas secundarias, metadatos y barra de estado (>= 4.5:1) |
| `border` | `#D4D9E2` | `#2F3541` | `#FFFFFF` | Divisores `SplitPane`, bordes de entrada y contornos (>= 3:1) |
| `danger` | `#C92A2A` | `#FF6B6B` | `#FF4D4D` | Errores de validacion, alertas criticas y acciones destructivas |
| `warning` | `#B45309` | `#F59F00` | `#FFD43B` | Advertencias recuperables y estado de cambios sin guardar |
| `success` | `#1E7E34` | `#51CF66` | `#00FF7F` | Confirmacion de guardado local, integridad o pruebas en verde |

---

## 2. Tipografia, Espaciado, Radios y Densidad

- **Display:** `"Segoe UI Variable Display", "SF Pro Display", "Inter", sans-serif` (titulos de ventana y secciones `16px-20px`, peso `600`)
- **UI:** `"Segoe UI Variable Text", "SF Pro Text", "Inter", "Noto Sans", sans-serif` (controles, menus y grillas `12px-14px`; barra de estado `11px`)
- **Monospace:** `"JetBrains Mono", "Cascadia Mono", "SF Mono", monospace` (rutas locales, logs, IDs y cifras tabulares `tnum`)
- **Espaciado (DIP/dp):** `xs: 4dp`, `sm: 8dp`, `md: 12dp`, `lg: 16dp`, `xl: 24dp`
- **Radios:** `sm: 3dp`, `md: 6dp`, `lg: 8dp`
- **Elevacion y Contorno:** En modo `light`/`dark`, separacion prioritaria mediante `1px` solido de `border` y elevacion minima (`0dp` base, `2dp` popover, `6dp` dialogo modal). En `high-contrast`, sombras desactivadas y bordes solidos `>= 1px`.
- **Modos de Densidad (`density_modes`):**
  - `compact`: Altura de fila `24dp`, altura de control `24dp`, padding horizontal `6dp`.
  - `standard`: Altura de fila `32dp`, altura de control `28dp`, padding horizontal `10dp`.
  - `comfortable`: Altura de fila `40dp`, altura de control `34dp`, padding horizontal `14dp`.
- **Movimiento y Preferencias del SO:** Transiciones funcionales `100ms-150ms` para paneles colapsables; `0ms` inmediato cuando el SO reporta animaciones reducidas activas.

---

## 3. Mapeo a Recursos Nativos

Los tokens anteriores son neutros respecto al toolkit y pueden exportarse opcionalmente a formato **W3C DTCG** (`design-tokens.tokens.json`) para generar diccionarios nativos:

### XAML `ResourceDictionary` (.NET: WPF / WinUI 3 / Avalonia / MAUI Desktop)
```xml
<ResourceDictionary xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <ResourceDictionary.ThemeDictionaries>
    <ResourceDictionary x:Key="Light">
      <SolidColorBrush x:Key="BgBaseBrush" Color="#F5F6F8" />
      <SolidColorBrush x:Key="SurfaceBrush" Color="#FFFFFF" />
      <SolidColorBrush x:Key="PrimaryBrush" Color="#0F52BA" />
      <SolidColorBrush x:Key="TextMainBrush" Color="#181B20" />
      <SolidColorBrush x:Key="BorderBrushToken" Color="#D4D9E2" />
    </ResourceDictionary>
    <ResourceDictionary x:Key="Dark">
      <SolidColorBrush x:Key="BgBaseBrush" Color="#111317" />
      <SolidColorBrush x:Key="SurfaceBrush" Color="#1A1D23" />
      <SolidColorBrush x:Key="PrimaryBrush" Color="#4C8DFF" />
      <SolidColorBrush x:Key="TextMainBrush" Color="#F1F3F5" />
      <SolidColorBrush x:Key="BorderBrushToken" Color="#2F3541" />
    </ResourceDictionary>
    <ResourceDictionary x:Key="HighContrast">
      <SolidColorBrush x:Key="BgBaseBrush" Color="#000000" />
      <SolidColorBrush x:Key="SurfaceBrush" Color="#000000" />
      <SolidColorBrush x:Key="PrimaryBrush" Color="#FFFF00" />
      <SolidColorBrush x:Key="TextMainBrush" Color="#FFFFFF" />
      <SolidColorBrush x:Key="BorderBrushToken" Color="#FFFFFF" />
    </ResourceDictionary>
  </ResourceDictionary.ThemeDictionaries>
</ResourceDictionary>
```

### Qt QSS / `QPalette` (PySide6 / PyQt6 / Qt C++)
```python
# Inyeccion parametrizada por modo (light | dark | high-contrast) desde tokens
PALETTE_MAP = {
    "light": {"bg_base": "#F5F6F8", "surface": "#FFFFFF", "primary": "#0F52BA", "text_main": "#181B20", "border": "#D4D9E2"},
    "dark": {"bg_base": "#111317", "surface": "#1A1D23", "primary": "#4C8DFF", "text_main": "#F1F3F5", "border": "#2F3541"},
    "high-contrast": {"bg_base": "#000000", "surface": "#000000", "primary": "#FFFF00", "text_main": "#FFFFFF", "border": "#FFFFFF"},
}
QSS_TEMPLATE = """
QMainWindow {{ background-color: {bg_base}; color: {text_main}; }}
QFrame#SidePanel {{ background-color: {surface}; border-right: 1px solid {border}; }}
QPushButton#PrimaryAction {{ background-color: {primary}; color: {surface}; border: 1px solid {border}; }}
"""
```

### Compose `MaterialTheme` / `CompositionLocal` (JVM Compose Desktop)
```kotlin
private val LightColorScheme = lightColorScheme(
    background = Color(0xFFF5F6F8),
    surface = Color(0xFFFFFFFF),
    primary = Color(0xFF0F52BA),
    onBackground = Color(0xFF181B20),
    outline = Color(0xFFD4D9E2),
    error = Color(0xFFC92A2A)
)

private val DarkColorScheme = darkColorScheme(
    background = Color(0xFF111317),
    surface = Color(0xFF1A1D23),
    primary = Color(0xFF4C8DFF),
    onBackground = Color(0xFFF1F3F5),
    outline = Color(0xFF2F3541),
    error = Color(0xFFFF6B6B)
)
```

### Slint (`global Theme` nativo en Rust)
```slint
export global Theme {
    in-out property <bool> dark-mode: false;
    in-out property <bool> high-contrast: false;
    out property <color> bg-base: high-contrast ? #000000 : (dark-mode ? #111317 : #F5F6F8);
    out property <color> surface: high-contrast ? #000000 : (dark-mode ? #1A1D23 : #FFFFFF);
    out property <color> primary: high-contrast ? #FFFF00 : (dark-mode ? #4C8DFF : #0F52BA);
    out property <color> text-main: high-contrast ? #FFFFFF : (dark-mode ? #F1F3F5 : #181B20);
    out property <color> border: high-contrast ? #FFFFFF : (dark-mode ? #2F3541 : #D4D9E2);
    out property <length> space-sm: 8px;
    out property <length> space-md: 12px;
}
```

---

## Historial de Revisiones (Ultimos Cambios)

| Version | Fecha | Requerimiento | Resumen del Cambio |
| :--- | :--- | :--- | :--- |
| `v0.1.0` | 2026-11-24 | `INIT` | Catalogo inicial multi-tema (`light`, `dark`, `system`, `high-contrast`), densidad desktop, `window_chrome` y mapeo a toolkits nativos. |

> *Nota: Esta tabla mantiene una ventana deslizante de los ultimos 3 cambios. Para el historial completo, consultar [`docs/backlog/changelog.md`](../backlog/changelog.md).*
