---
artifact_type: tech-stack
---

# Tech Stack

## Ecosistema Hibrido
- **Lenguaje**: Rust (Core) + TypeScript (UI WebView)
- **Framework UI**: `Tauri v2` (WebView nativo del SO)
- **Empaquetado y Manifiesto**: `src-tauri/Cargo.toml` (`version = "0.1.0"`) y `package.json`
- **Base de Datos Embebida**: `SQLite (WAL)` via `rusqlite`
- **Pruebas**: `cargo test` (core) y `playwright` (UI)

## Dependencias
- `tauri` `2.0`
- `serde` / `serde_json`
- `@tauri-apps/api` `^2.0.0`
