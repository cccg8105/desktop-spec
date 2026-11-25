# Guias de Diseno para Escritorio Nativo (Anti-AI Slop y Ergonomia Desktop)

Este documento rige la calidad visual, ergonomica, cromatica y de accesibilidad de toda interfaz nativa generada bajo `desktop-spec` (WPF, WinUI 3, Avalonia, MAUI Desktop, PySide6/PyQt6, Flet, Compose Desktop, JavaFX, Slint/Iced/egui y Qt C++), eliminando el "AI Slop" web empacado en ventanas de escritorio.

---

## 1. Prohibiciones Estrictas (Eliminando el "AI Slop" en Escritorio)

- **Prohibido "Landing Page / Web SaaS" Dentro de una Ventana:** No construyas *hero banners* gigantes, cabeceras publicitarias, margenes laterales vacios de pagina web ni rejillas uniformes de 3 tarjetas blancas identicas con sombra difusa. Una aplicacion de escritorio nativa es una **herramienta operativa**, no un folleto comercial.
- **Prohibido Degradados Purpura/Indigo Genericos:** Nada de fondos o botones con degradados llamativos (`#6366F1` -> `#9333EA`) sin justificacion de identidad de marca ni teñido arbitrario de palabras en titulos.
- **Prohibido Hardcodear Colores, Fuentes o Tamanos Fuera de `tokens-and-themes.md`:** Todo valor visual debe provenir de los tokens semanticos mapeados al mecanismo nativo del toolkit (`DynamicResource` / `ThemeResource` en XAML, `QPalette` / QSS parametrizado en Qt, `MaterialTheme` / `CompositionLocal` en Compose, tokens en Slint/Iced).
- **Prohibido Ignorar el Cromo y Convenciones del Sistema Operativo:** Respeta las barras de menu, dialogos nativos de archivo, orden de botones de dialogo por plataforma y barras de desplazamiento nativas, salvo cuando `window_chrome.titlebar_style` en `tokens-and-themes.md` especifique un titulo integrado debidamente probado en Windows, macOS y Linux.
- **Prohibido Iconos Decorativos Sin Significado:** Cada icono en barras de herramientas o paneles debe representar una accion o estado claro, acompanado de etiqueta legible o tooltip que incluya su atajo de teclado.

---

## 2. Densidad de Herramienta Profesional y Paneles Divididos

- **Arquitectura Espacial por Regiones Funcionales (Split Panes):** Prioriza la disposicion ergonomica de escritorio con divisores redimensionables (`Splitter` / `SplitPane` / `QSplitter`):
  - Barra de herramientas o comandos en la franja superior.
  - Panel de navegacion o explorador lateral colapsable y redimensionable.
  - Area central de trabajo de maxima prioridad (editor, lienzo o tabla virtualizada).
  - Panel inspector contextual secundario (opcional y colapsable).
  - Barra de estado inferior (`StatusBar`) para metricas activas, modo, ruta o progreso en segundo plano sin interrumpir al usuario.
- **Modos de Densidad Declarados (`density_modes`):**
  - `compact`: Para herramientas de alta densidad informativa, consolas, logs, tablas financieras o IDEs (altura de fila ~24-28px, padding 4-6px).
  - `standard`: Densidad equilibrada por defecto para productividad general (altura de fila ~32-36px, controles de ~28-32px).
  - `comfortable`: Mayor respiro espacial para herramientas creativas o usuarios que requieren objetivos de puntero mas amplios (altura de fila ~40-44px, padding 12-16px).
- **Geometria de Ventana y Escalado Multi-DPI (Sin Mobile-First Web):**
  - No existen breakpoints web mobile-first (`390x844`). Toda ventana define `window_geometry` (`min_width_px`, `min_height_px`, `resizable`) acorde a su tarea (ej. `960x640` ventana principal, `480x360` dialogos).
  - Cada panel gestiona su propio scroll interno cuando hay desbordamiento; la ventana raiz nunca debe comportarse como una pagina web con scroll vertical unico de extremo a extremo.
  - Diseno 100% independiente de resolucion logica (*DIP/dp*) para escalado limpio al `100%`, `125%`, `150%` y `200%` DPI sin recortes de texto ni iconos pixelados (preferir geometria vectorial / SVG / iconos por escala).

---

## 3. Temas del Sistema Operativo (`light`, `dark`, `system`, `high-contrast`)

- **Paleta Semantica Restringida (4 a 6 Hex Base + Estados):** Define en `docs/design/tokens-and-themes.md` una paleta sobria y coherente (`bg-base`, `surface`, `surface-elevated`, `primary`, `text-main`, `text-muted`, `border`, `danger`, `warning`, `success`).
- **Cuatro Modos Obligatorios de Soporte:**
  - `light` y `dark`: Simetria estricta garantizando contraste **WCAG AA** (`>= 4.5:1` en texto normal, `>= 3:1` en bordes de controles e indicadores de foco, `>= 7:1` recomendado en lectura prolongada).
  - `system`: Suscripcion reactiva en tiempo real al cambio de apariencia del sistema operativo (Windows `UISettings`, macOS `NSAppearance`, Linux XDG Desktop Portal `color-scheme`) sin reiniciar la aplicacion.
  - `high-contrast`: Obligatorio para accesibilidad nativa (Windows High Contrast, macOS Increase Contrast, Linux HighContrast). Debe asignar `high_contrast_hex` de alto contraste o mapear a pinceles del sistema, eliminando dependencias de sombras difusas y garantizando bordes solidos (`>= 1px`) en todos los controles y paneles.

---

## 4. Tipografia Nativa y Legibilidad en Datos

- **Maximo 2 Familias Tipograficas + Monospace Tecnica:**
  - `ui_font`: Fuente nativa del sistema operativo (`Segoe UI Variable` / `Segoe UI` en Windows, `SF Pro Text` / `-apple-system` en macOS, `Inter` / `Cantarell` / `Noto Sans` en Linux) en rangos desktop nitidos (`12px-14px` para formularios, menus y tablas; `11px` en status bar y metadatos).
  - `display_font`: Encabezados de ventana, secciones y dialogos (`16px-22px`) con jerarquia clara por peso y espaciado, sin tamanos desproporcionados de *marketing web*.
  - `mono_font`: Obligatoria para codigos, identificadores, rutas de archivos, registros de log, atajos de teclado y columnas numericas (`JetBrains Mono`, `Cascadia Mono`, `SF Mono`), usando cifras tabulares (`tnum` / `TabularNums`) para alinear numeros verticalmente.

---

## 5. Movimiento Intencional Respetando Ajustes del SO

- **Velocidad de Herramienta Profesional:** La respuesta ante seleccion, tecleo y cambio de pestanas debe sentirse instantanea (`0ms` o `< 100ms`). Usa transiciones breves (`100ms-150ms`) solo para orientar cambios de estado en paneles colapsables o flyouts; nunca animaciones lentas (`> 250ms`) que entorpezcan flujos repetitivos.
- **Respeto Obligatorio a Movimiento Reducido del SO:** Consulta la preferencia nativa del sistema (`UISettings.AnimationsEnabled` / `SystemParameters.ClientAreaAnimation` en Windows, `NSWorkspace.accessibilityDisplayShouldReduceMotion` en macOS, `gtk-enable-animations` / portal en Linux). Cuando este desactivada, todas las transiciones deben colapsar automaticamente a `0ms`.

---

## 6. Foco Nativo, Accesibilidad del SO y Atajos por Plataforma (`Ctrl` vs `Cmd`)

- **Anillo de Foco Visible y Orden Logico:** Todo control enfocable debe mostrar un indicador de foco de alto contraste al navegar por teclado (`Tab`, `Shift+Tab`, flechas en listas/arboles/grillas, `Enter`/`Space` para activar, `Escape` para cerrar o cancelar y restaurar el foco al disparador).
- **Roles y Etiquetas del SO:** Configura `AutomationProperties.Name` (XAML), `accessibleName` / `accessibleDescription` (Qt), `semantics { contentDescription = ... }` (Compose) o equivalente nativo en todo boton de solo icono, divisor de panel, tabla e indicador de estado para compatibilidad con Narrator, VoiceOver y Orca.
- **Convenciones Multiplataforma de Atajos:** Parametriza siempre el modificador primario (`Ctrl` en Windows/Linux, `Cmd` en macOS) y adapta atajos propios del SO:

| Accion Estandar | Windows / Linux | macOS |
| :--- | :--- | :--- |
| Nuevo / Abrir / Guardar | `Ctrl+N` / `Ctrl+O` / `Ctrl+S` | `Cmd+N` / `Cmd+O` / `Cmd+S` |
| Buscar / Paleta de comandos | `Ctrl+F` / `Ctrl+K` (o `Ctrl+Shift+P`) | `Cmd+F` / `Cmd+K` (o `Cmd+Shift+P`) |
| Preferencias / Ajustes | `Ctrl+,` | `Cmd+,` |
| Cerrar pestana o vista activa | `Ctrl+W` | `Cmd+W` |
| Salir de la aplicacion | `Alt+F4` (Win) / `Ctrl+Q` (Linux) | `Cmd+Q` |

---

## 7. Microcopy Directo, Errores Accionables e i18n

- **Etiquetas de Accion Precisas:** Botones con verbo y sustantivo especificos (*"Guardar proyecto"*, *"Exportar CSV"*, *"Descartar cambios"*). Prohibido microcopy grandilocuente o ambiguo (*"Comienza tu viaje"*, *"Potencia tu flujo"*).
- **Titulo de Ventana Informativo:** Refleja el recurso activo y el indicador de cambios sin guardar (ej. `presupuesto.db* - NombreApp`).
- **Mensajes de Error Accionables:** En una linea clara explicando causa local y salida de recuperacion (*"No se pudo guardar 'reporte.pdf': el archivo esta abierto en otro programa. [Reintentar] [Guardar como...]"*).
- **Externalizacion i18n:** Si `docs/technical/tech-stack.md` habilita multiples idiomas, prohibe concatenar cadenas literales en vistas o ViewModels; utiliza diccionarios de recursos locales (`.resx`, `.qm`, `strings.xml`, Fluent).
