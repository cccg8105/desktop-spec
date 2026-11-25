---
name: desktop-release
description: "Gobierna pipelines CI/CD multi-SO (windows-latest, macos-latest, ubuntu-latest), empaquetado nativo, Code Signing & Notarization sin secretos en repo/binario, canales beta/stable, Auto-Updater y auditoria gh."
---

# desktop-release Skill

Activa esta skill bajo demanda cuando una tarea cree o modifique pipelines CI/CD (`.github/workflows/`), instaladores nativos, configuracion de **Code Signing & Notarization**, canales de actualizacion, **Auto-Updater** o prepare un corte de release/tag `vX.Y.Z`.

---

## 1. Matriz Multi-SO y Modelo de Ramas
- **Matriz CI Obligatoria (`.github/workflows/`):** Compila, prueba y empaqueta en corredores nativos segun `target_platforms` de `docs/technical/packaging-and-release.md`:
  - `windows-latest` -> `MSIX`, `WiX` (`.msi`) o `InnoSetup` (`.exe`).
  - `macos-latest` -> `.dmg` / `.pkg` (arquitecturas `arm64` / `x64` / universal).
  - `ubuntu-latest` -> `AppImage`, `Flatpak` o `.deb` / `.rpm`.
- **Promocion por defecto:**
  - `PR` -> CI de validacion (`desktop-spec check`, tests de arquitectura/dominio/UI headless en matriz multi-SO).
  - `main` -> Compilacion de artefactos de canal **`beta`** (pre-release / nightly controlado).
  - `tag vX.Y.Z` -> Compilacion firmada, notarizada y publicada en canal **`stable`** con artefactos y manifiesto de checksums `SHA256SUMS.txt`.
- **Workflow Gestionado:** Nunca sobreescribas `.github/workflows/desktop-spec-check.yml` si conserva `# DESKTOP-SPEC-CI-MANAGED` en la linea 1.

---

## 2. Code Signing, Notarization y Cero Secretos en Repo o Binario
1. **Separacion estricta `vars.*` vs. `secrets.*`:**
   - Parametros no sensibles (`APP_CHANNEL`, `UPDATE_FEED_URL`, `APPLE_TEAM_ID`, `SIGNING_TIMESTAMP_URL`) -> GitHub Variables (`${{ vars.NOMBRE }}`).
   - Certificados, contrasenias, llaves privadas y credenciales de notarizacion (`WINDOWS_PFX_BASE64`, `WINDOWS_PFX_PASSWORD`, `APPLE_CERT_P12_BASE64`, `APPLE_CERT_PASSWORD`, `APPLE_APP_SPECIFIC_PASSWORD`, `LINUX_GPG_KEY`) -> exclusivamente **GitHub Secrets** (`${{ secrets.NOMBRE }}`) o Vault/OIDC efimero en el runner.
   - **Prohibido** versionar archivos `.pfx`, `.p12`, `.keystore`, `.jks`, `.pem` o `.key` en Git, o embeber secretos de build dentro del binario nativo compilado.
2. **Firma por Plataforma:**
   - **Windows (Authenticode):** Importa el certificado en memoria/almacen temporal del runner, firma el ejecutable y el instalador (`signtool` / Azure Trusted Signing) con servidor de timestamp y limpia artefactos temporales tras el paso.
   - **macOS (Codesign + Notarization):** Firma con `Developer ID Application` (`--options runtime --timestamp`), empaqueta `.dmg`/`.pkg`, envia a `xcrun notarytool submit --wait` y ejecuta `xcrun stapler staple`.
   - **Linux:** Firma artefactos/checksums (GPG o minisign/cosign) y publica metadatos verificables.
3. **Sincronizacion de Variables (`build_env_vars`):** Toda variable o secreto requerido para build/empaquetado debe registrarse simultaneamente bajo un `REQ-DESK-*` activo en:
   - `docs/technical/packaging-and-release.md` (tabla `build_env_vars`).
   - `.env.example` (solo nombres no sensibles de configuracion local, sin secretos).
   - `.github/workflows/*.yml` (`vars.*` / `secrets.*`).

---

## 3. Canales `beta`/`stable`, Auto-Updater y Recuperacion Local
1. **Canales de Distribucion:** Separa manifiestos de actualizacion (`beta` vs `stable`) para permitir validacion previa antes de promocionar a usuarios finales.
2. **Auto-Updater Seguro:**
   - Verifica siempre firma criptografica y digest **SHA-256** del paquete descargado antes de aplicar la actualizacion.
   - Ejecuta la descarga en segundo plano sin bloquear el hilo UI; aplica la sustitucion al reiniciar o mediante helper nativo con **respaldo previo de la base de datos local** (`.db`) antes de correr migraciones de la nueva version.
3. **Politica de Recuperacion ante Fallos:** Si la instalacion falla o la nueva version no arranca, conserva la version previa o instruye recuperacion limpia sin perder datos del usuario en `%APPDATA%` / `~/Library/Application Support` / `$XDG_DATA_HOME`.

---

## 4. Auditoria Pre-Release con GitHub CLI (`gh`)
Antes de cortar un tag `vX.Y.Z` o habilitar un canal `beta`/`stable`, verifica que existan todas las variables y secretos configurados sin exponer sus valores:

```bash
gh auth status
gh variable list
gh secret list
gh variable list --env beta
gh secret list --env beta
gh variable list --env stable
gh secret list --env stable
```

Si falta una llave de firma, certificado de notarizacion o variable declarada en `docs/technical/packaging-and-release.md`, deten el corte de release e informa al usuario.

---

## 5. Checklist de Corte de Release
1. Verifica que `desktop-spec check` (o `dspec check`), los tests de arquitectura modular, dominio/BD y UI headless pasen al 100% en las plataformas objetivo.
2. Ejecuta la auditoria `gh variable list` / `gh secret list` para el entorno destino (`beta` o `stable`).
3. Cierra el requerimiento final del hito actualizando la version en el manifiesto nativo (`*.csproj`, `pyproject.toml`, `build.gradle*`, `Cargo.toml`, `CMakeLists.txt`) mediante:
   `dspec resolve <REQ-DESK-ID> --bump`
4. Crea el tag anotado sobre `main` y publica:
   `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
   `git push origin main --follow-tags`
5. Verifica en GitHub Actions que la matriz `windows-latest`, `macos-latest` y `ubuntu-latest` genere los instaladores firmados y el archivo `SHA256SUMS.txt`.
