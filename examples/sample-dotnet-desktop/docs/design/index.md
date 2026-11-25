# Indice del Sistema de Diseno Nativo — sample-dotnet-desktop

> **Instruccion para el Agente de IA:**
> Toda decision visual, cromatica, tipografica, de densidad operativa, movimiento o cromo de ventana debe validarse contra estos artefactos antes de escribir vistas o recursos nativos.
> - Reglas visuales Anti-AI Slop desktop, densidad y accesibilidad del SO: [`design-guidelines.md`](../../.spec/templates/design-guidelines.md)
> - Catalogo activo de tokens, temas y mapeo nativo: [`tokens-and-themes.md`](./tokens-and-themes.md)
> - Molde de referencia de tokens: [`_template_design_tokens.md`](../../.spec/templates/_template_design_tokens.md)

---

## Artefactos de Identidad Visual Desktop

| Artefacto | Archivo | Responsabilidad |
| :--- | :--- | :--- |
| **Tokens y Temas Nativos** | [tokens-and-themes.md](./tokens-and-themes.md) | Paleta semantica (`light`, `dark`, `system`, `high-contrast`), tipografia nativa + monospace tabular, densidad (`compact`, `standard`, `comfortable`), `window_chrome` y mapeo a XAML, Qt, Compose y Slint. |
| **Guias Anti-AI Slop Desktop** | [design-guidelines.md](../../.spec/templates/design-guidelines.md) | Ergonomia de paneles divididos, escalado multi-DPI, respeto a animaciones reducidas del SO, foco visible, roles de accesibilidad OS y atajos `Ctrl` vs `Cmd`. |

---

## Resumen de Tokens Activos

<!-- SYNC:DESIGN_TOKENS_SUMMARY:START -->
- **Modos de tema activos:** `light`, `dark`, `system`, `high-contrast` (11 tokens cromaticos semanticos).
- **Modos de densidad desktop:** `compact`, `standard`, `comfortable`.
- **Tipografias:** `"Segoe UI Variable Display", "SF Pro Display", "Inter", sans-serif` (titulos de ventana y secciones `16px-20px`, peso `600`) (display/UI) y `"JetBrains Mono", "Cascadia Mono", "SF Mono", monospace` (rutas locales, logs, IDs y cifras tabulares `tnum`) (monoespacio tabular).
- **Regla estricta:** Prohibido hardcodear colores hex, tamanos o estilos fuera del catalogo semantico definido en [`tokens-and-themes.md`](./tokens-and-themes.md).
<!-- SYNC:DESIGN_TOKENS_SUMMARY:END -->
