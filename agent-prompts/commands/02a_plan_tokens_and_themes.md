# Comando: 02a_plan_tokens_and_themes

> **Proposito:** Definir o extender los tokens semanticos de diseno nativo, temas del sistema operativo y modos de densidad desktop (Etapa 2A).

## Instrucciones para el Agente:
1. Revisa `docs/design/tokens-and-themes.md`, `.spec/templates/_template_design_tokens.md` y `.spec/templates/design-guidelines.md`.
2. Evalua si los tokens semanticos vigentes cubren el requerimiento; evita proliferar nuevos colores hex sin rol semantico claro.
3. Si se requieren nuevos tokens:
   - Define equivalentes simetricos para `light`, `dark` y soporte `high-contrast`, respetando la integracion con `system` del SO y contraste WCAG AA (`>= 4.5:1` texto normal, `>= 3:1` controles y bordes).
   - Define impacto en modos de densidad desktop (`compact`, `standard`, `comfortable`), tipografia del sistema/embebida (`Display`, `UI`, `Monospace`), espaciados, radios, elevacion y `window_chrome` (`titlebar_style`, `backdrop_material`, `corner_style`).
   - Documenta el mapeo hacia recursos nativos del ecosistema (`{{ECOSYSTEM_NAME}}` / `{{UI_TOOLKIT}}`): XAML `ResourceDictionary`, Qt `QSS`/`QPalette`, Compose `MaterialTheme` o Slint, y exportacion neutra W3C DTCG (`*.tokens.json`) si aplica.
   - Asegura respeto a preferencias de movimiento reducido del SO en animaciones y transiciones de paneles.
4. Actualiza `## Historial de Revisiones (Ultimos Cambios)` (maximo 3 filas) en `docs/design/tokens-and-themes.md` y ejecuta `dspec sync` para actualizar `docs/design/index.md`.
