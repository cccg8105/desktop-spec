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

# Blueprint: Sistema de Tokens y Temas Nativos Desktop

> Define la paleta semantica multi-tema (`light`, `dark`, `system`, `high-contrast`), tipografia nativa y monoespaciada tabular, densidad operativa, cromo de ventana y traduccion a recursos nativos (.NET XAML, Qt QSS/`QPalette`, Compose `MaterialTheme` y Slint), sin acoplamiento web ni resoluciones fijas.

---

## 1. Colores Semanticos

| Token | Modo Claro | Modo Oscuro | Alto Contraste | Rol de Uso |
| :--- | :--- | :--- | :--- | :--- |
| `bg-base` | `#F5F6F8` | `#111317` | `#000000` | Fondo base de ventana raiz y area de trabajo |
| `surface` | `#FFFFFF` | `#1A1D23` | `#000000` | Paneles laterales, inspectores y formularios |
| `surface-elevated` | `#F0F2F5` | `#232730` | `#1A1A1A` | Menus contextuales, popovers, dialogos y cabeceras |
| `primary` | `#0F52BA` | `#4C8DFF` | `#FFFF00` | Accion primaria, seleccion e indicador de foco |
| `primary-hover` | `#0B3E91` | `#70A5FF` | `#FFFFFF` | Estado hover o activo de accion primaria |
| `text-main` | `#181B20` | `#F1F3F5` | `#FFFFFF` | Texto operativo principal y titulos (>= 7:1) |
| `text-muted` | `#4E5866` | `#9AA4B2` | `#E0E0E0` | Etiquetas secundarias y barra de estado (>= 4.5:1) |
| `border` | `#D4D9E2` | `#2F3541` | `#FFFFFF` | Divisores `SplitPane` y bordes solidos (>= 3:1) |
| `danger` | `#C92A2A` | `#FF6B6B` | `#FF4D4D` | Errores de validacion y acciones destructivas |
| `warning` | `#B45309` | `#F59F00` | `#FFD43B` | Advertencias y cambios sin guardar |
| `success` | `#1E7E34` | `#51CF66` | `#00FF7F` | Confirmacion de operaciones locales exitosas |

---

## 2. Tipografia, Espaciado, Radios y Densidad

- **Display:** `"Segoe UI Variable Display", "SF Pro Display", "Inter", sans-serif` (encabezados de ventana y secciones `16px-20px`, peso `600`)
- **UI:** `"Segoe UI Variable Text", "SF Pro Text", "Inter", "Noto Sans", sans-serif` (controles, menus y tablas `12px-14px`; status bar `11px`)
- **Monospace:** `"JetBrains Mono", "Cascadia Mono", "SF Mono", monospace` (IDs, rutas de archivo, logs y cifras tabulares `tnum`)
- **Espaciado (DIP/dp):** `xs: 4dp`, `sm: 8dp`, `md: 12dp`, `lg: 16dp`, `xl: 24dp`
- **Radios:** `sm: 3dp`, `md: 6dp`, `lg: 8dp`
- **Elevacion:** `none: 0dp`, `popover: 2dp`, `dialog: 6dp` (desactivada en `high-contrast`, usando bordes solidos `>= 1px`)
- **Modos de Densidad (`density_modes`):**
  - `compact`: Fila `24dp`, control `24dp`, padding horizontal `6dp`.
  - `standard`: Fila `32dp`, control `28dp`, padding horizontal `10dp`.
  - `comfortable`: Fila `40dp`, control `34dp`, padding horizontal `14dp`.
- **Exportacion Neutra W3C DTCG (`*.tokens.json`, opcional):**
  ```json
  {
    "color": {
      "bg-base": { "$type": "color", "$value": "#F5F6F8" },
      "surface": { "$type": "color", "$value": "#FFFFFF" },
      "primary": { "$type": "color", "$value": "#0F52BA" }
    }
  }
  ```

---

## 3. Mapeo a Recursos Nativos

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
THEME_TOKENS = {
    "light": {"bg_base": "#F5F6F8", "surface": "#FFFFFF", "primary": "#0F52BA", "text_main": "#181B20", "border": "#D4D9E2"},
    "dark": {"bg_base": "#111317", "surface": "#1A1D23", "primary": "#4C8DFF", "text_main": "#F1F3F5", "border": "#2F3541"},
    "high-contrast": {"bg_base": "#000000", "surface": "#000000", "primary": "#FFFF00", "text_main": "#FFFFFF", "border": "#FFFFFF"},
}
```

### Compose `MaterialTheme` (JVM Compose Desktop)
```kotlin
private val LightColors = lightColorScheme(
    background = Color(0xFFF5F6F8),
    surface = Color(0xFFFFFFFF),
    primary = Color(0xFF0F52BA),
    onBackground = Color(0xFF181B20),
    outline = Color(0xFFD4D9E2),
    error = Color(0xFFC92A2A)
)

private val DarkColors = darkColorScheme(
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
}
```

---

## Historial de Revisiones (Ultimos Cambios)

| Version | Fecha | Requerimiento | Resumen del Cambio |
| :--- | :--- | :--- | :--- |
| `v0.1.0` | YYYY-MM-DD | `INIT` | Definicion inicial de tokens multi-tema, densidad desktop, `window_chrome` y mapeo nativo. |

> *Nota: Esta tabla mantiene una ventana deslizante de los ultimos 3 cambios. Para el historial completo, consultar [`docs/backlog/changelog.md`](../backlog/changelog.md).*
