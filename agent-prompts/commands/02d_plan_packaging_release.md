# Comando: 02d_plan_packaging_release

> **Proposito:** Auditar presupuestos de rendimiento desktop, politicas de seguridad local y estrategia de empaquetado nativo, firma y distribucion (Etapa 2D).

## Instrucciones para el Agente:
1. Consulta `docs/technical/tech-stack.md` y `.spec/templates/_template_tech_stack.md`:
   - Evalua impacto en los presupuestos desktop (`cold_startup_ms`, `idle_ram_mb`, `ui_frame_budget_ms <= 16`, `installer_max_mb`).
   - Verifica politicas de seguridad local: resguardo exclusivo de credenciales en **OS Keyring**, canonizacion de rutas contra **Path Traversal**, **deserializacion segura** y endurecimiento del binario (`binary_hardening`).
2. Activa la skill `.spec/skills/desktop-release/SKILL.md` (o su ruta instalada en el harness) y consulta `docs/technical/packaging-and-release.md` junto con `.spec/templates/_template_packaging_release.md`:
   - Actualiza la matriz CI multi-SO (`windows-latest`, `macos-latest`, `ubuntu-latest`) y el diagrama `pipeline_diagram_mermaid`.
   - Verifica formatos nativos por plataforma (`MSIX`/`WiX`/`InnoSetup`, `.dmg`/`.pkg`, `AppImage`/Flatpak/DEB), configuracion de **Code Signing & Notarization** (certificados en `secrets.*`, nunca en repositorio ni en binario) y verificacion SHA-256.
   - Si se agregan variables/secretos de build o firma (`build_env_vars`), sincronizalos entre `packaging-and-release.md`, `.github/workflows/*.yml` y audita previamente con `gh variable list` / `gh secret list`.
   - Revisa canales de distribucion (`beta`/`stable`), configuracion de **Auto-Updater** y politica de recuperacion ante fallo de actualizacion.
3. Actualiza `## Historial de Revisiones (Ultimos Cambios)` manteniendo maximo 3 filas y valida con `dspec check`.
