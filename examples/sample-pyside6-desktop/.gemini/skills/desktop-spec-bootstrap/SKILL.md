---
name: desktop-spec-bootstrap
description: "Guia el onboarding asistido de aplicaciones de escritorio nativas existentes (Brownfield) en 4 fases mediante ingenieria inversa estructurada y checklist persistente en .spec/bootstrap-report.md."
---

# desktop-spec-bootstrap Skill

Esta skill guia al agente en la adopcion ordenada de `desktop-spec` sobre repositorios desktop nativos existentes (`.NET`: `wpf`, `winui3`, `avalonia`, `maui-desktop`; `Python`: `pyside6`, `pyqt6`, `flet`; `JVM`: `compose-desktop`, `javafx`; `Rust / C++`: `rust-native`, `qt-cpp`) con deuda modular, UI acoplada a persistencia o documentacion desfasada.

## Regla de Oro Anti-Perdida de Contexto
1. **Memoria en Disco (`.spec/bootstrap-report.md`):** Registra y consulta el avance en una lista de verificacion GPS (`- [ ]` / `- [x]`) dividida por dominios, modulos y documentos tecnicos.
2. **Un Bloque por Turno:** Documenta un artefacto o modulo a la vez y marca `[x]` inmediatamente tras completarlo para sobrevivir compactaciones de contexto.

---

## Flujo Operativo en 4 Fases

### Fase 1: Diagnostico del Ecosistema y Linea Base
1. Inspecciona los manifiestos reales (`*.csproj`, `pyproject.toml`, `setup.cfg`, `build.gradle.kts`, `build.gradle`, `pom.xml`, `Cargo.toml`, `CMakeLists.txt`), dependencias de toolkit UI, base de datos embebida y pruebas existentes.
2. Actualiza `.spec/config.yaml` y `docs/technical/tech-stack.md` reflejando el ecosistema real (`{{ECOSYSTEM_NAME}}` / `{{UI_TOOLKIT}}`), presupuestos desktop medibles y `test_baseline` (`none`, `partial`, `solid`).
3. Si existe `graphify-out/graph.json`, analiza *God Nodes* y comunidades entre modulos; si no existe, sugiere generar el grafo respetando `.graphifyignore`.

### Fase 2: Extraccion Tecnica e Identidad As-Is
**Regla de Verdad:** *El codigo fuente, los manifiestos y los esquemas locales mandan sobre cualquier documentacion antigua.*
1. **Tokens y Temas As-Is (`docs/design/tokens-and-themes.md`):** Extrae recursos XAML, QSS/QPalette, MaterialTheme o Slint reales, fuentes del sistema/embebidas y documenta si falta soporte `dark` o `high-contrast`.
2. **Arquitectura Modular (`docs/technical/modular-architecture.md`):** Inventaria modulos/paquetes reales `MOD-*`, sus fachadas (o ausencia de ellas), acoplamientos cruzados, Event Bus si existe y uso de hilos en segundo plano.
3. **Ventanas y Contratos OS (`docs/technical/windowing-and-os-contracts.md`):** Mapea ventanas/dialogos reales `WIN-*`, single-instance lock, atajos de teclado y puntos de integracion con el SO (dialogos de archivo, drag-and-drop, extensiones, system tray).
4. **Persistencia Local (`docs/technical/local-persistence.md`):** Extrae tablas SQLite/DuckDB/archivos de proyecto, rutas en disco (`%APPDATA%`, `Application Support`, `$XDG_DATA_HOME`) y mecanismo actual de migraciones on-startup.
5. **Empaquetado y Release (`docs/technical/packaging-and-release.md`):** Inventaria scripts de instaladores (`MSIX`/`WiX`/`InnoSetup`, `.dmg`, `AppImage`/Flatpak), workflows CI multi-SO y configuracion actual de firma.

### Fase 3: Seleccion Full vs. Progresivo (Strangler / Just-In-Time)
Pregunta al usuario (Pregunta de 2 a 4 decisiones por ronda en el chat colocando primero la opcion recomendada con trade-offs claros) si desea:
- **Modo Progresivo (Recommended):** Documentar los 1 o 2 pares `UF-*`/`UC-*` criticos y registrar el resto de modulos en `docs/functional/index.md` bajo `Modulos Legados Detectados` (`Pendiente As-Is`).
- **Modo Completo:** Documentar especificaciones `UF-*` y `UC-*` para todos los modulos y flujos detectados ahora.

### Fase 4: Triage de Deuda y Cierre sin Alterar Codigo Fuente
1. Si hay ambiguedad sobre si un comportamiento heredado es intencional (*As-Is*) o un defecto, resuelvelo con `/grill-me`. Registra en `docs/backlog/audit-proposals.md` (sin alterar codigo fuente) los hallazgos con formato `[AUDIT-DESK-DOMINIO-NUM]` y evidencia `archivo:L10-L25`:
   - Vistas o ViewModels llamando directamente a SQLite o archivos sin pasar por fachada de modulo `MOD-*`.
   - Dependencias ciclicas o imports cruzados entre internos de modulos.
   - Operaciones pesadas de I/O o CPU en el hilo principal de UI (violacion `NoMainThreadBlock`).
   - Secretos en archivos planos, falta de canonizacion contra Path Traversal o deserializacion insegura.
   - Migraciones locales sin respaldo previo ni validacion de `schema_version`.
   - Colores/fuentes quemadas fuera de tokens, falta de soporte `high-contrast` o fallos de accesibilidad nativa.
2. Marca completada la Fase 4 en `.spec/bootstrap-report.md`, ejecuta `dspec sync` y `dspec check` e informa al usuario.
