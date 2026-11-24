# Comando: 02c_plan_windowing_and_persistence

> **Proposito:** Especificar contratos de ventanas nativas (`WIN-*`), integracion con el sistema operativo y modelo de persistencia local embebida (Etapa 2C).

## Instrucciones para el Agente:
1. **Ventanas y Contratos del SO (`docs/technical/windowing-and-os-contracts.md` usando `.spec/templates/_template_windowing_os.md`):**
   - Verifica `window_topology` (`single-window`, `multi-window`, `mdi-tabs`, `tray-resident`) y politica `single_instance_policy` (lock + mecanismo IPC local).
   - Registra nuevas ventanas o dialogos (`WIN-[DOMINIO]-[NUM]`) enlazados a su `user_flow_id` (`UF-*`), geometria minima (`min_width_px`, `min_height_px`), guardia de cambios sin guardar (`unsaved_changes_guard`) y comportamiento al cerrar.
   - Actualiza la tabla de atajos globales (`shortcut_win_linux` vs `shortcut_macos` con `Ctrl` vs `Cmd`) e integraciones del SO (`file_dialogs`, `drag_and_drop`, `file_associations`, `deep_links`, `cli_arguments`, `system_tray`, `os_permissions`).
2. **Persistencia Local (`docs/technical/local-persistence.md` usando `.spec/templates/_template_local_persistence.md`):**
   - Actualiza el diagrama `erDiagram`, definicion de tablas y columnas (`owner_module`, claves `PK`/`FK`/`UK`, indices) o formatos de archivos de proyecto (`project_file_formats` con escritura atomica y campo `version_field`).
   - Verifica cumplimiento de rutas estandar del SO (`%APPDATA%`, `~/Library/Application Support`, `$XDG_DATA_HOME`) separando datos, cache y logs rotativos.
   - Exige estrategia de **migraciones automaticas on-startup** con idempotencia, respaldo preventivo previo (`pre_migration_backup: true`), validacion de `schema_version` y politica de recuperacion ante archivos de versiones futuras o corrupcion.
3. Actualiza `## Historial de Revisiones (Ultimos Cambios)` (maximo 3 filas) en ambos documentos y valida con `dspec check`.
