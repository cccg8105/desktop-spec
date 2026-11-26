# Guias de Frontera Funcional: `UF-*` vs. `UC-*` (`desktop-spec`)

Este documento establece la frontera normativa entre los **Flujos de Interaccion de Usuario (`docs/functional/user-flows/UF-*.md`)** y los **Casos de Uso de Dominio (`docs/functional/use-cases/UC-*.md`)** dentro de una aplicacion de escritorio nativa estructurada como monolito modular.

---

## 1. Regla de Oro de la Frontera

> **`UF-*` describe como interactua el usuario con ventanas, controles, foco, estados visuales y atajos del sistema operativo, y delega las operaciones de negocio mediante `invokes_use_case`. `UC-*` describe que reglas de negocio (`BR-*`), invariantes OCL, persistencia local y eventos internos ejecuta el modulo, sin conocer ventanas, toolkits graficos ni controles UI.**

La dependencia entre especificaciones es estrictamente **unidireccional**:

```text
[UF-* (Presentacion / Ventana / FSM UI)] --(invokes_use_case)--> [UC-* (Aplicacion / Dominio / Persistencia Local)]
```

Un `UC-*` **nunca** referencia ni depende de un `UF-*`.

---

## 2. Los Tres Escenarios Validos en `REQ-DESK-*`

Todo requerimiento `MAJOR` o `MINOR` en `docs/backlog/pending.md` debe encajar exactamente en uno de los siguientes tres escenarios:

| Escenario | Campo `scope` en `REQ-DESK-*` | `references.user_flows` | `references.use_cases` | Cuando se utiliza |
| :--- | :--- | :--- | :--- | :--- |
| **1. Dual (`UF -> UC`)** | `full-module` | 1 o mas `UF-*.md` existentes | 1 o mas `UC-*.md` existentes | Funcionalidad completa que combina interaccion en ventana/dialogo y reglas de negocio, calculos, persistencia local o eventos de dominio. El `UF-*` declara `invokes_use_case: UC-[MOD]-[NUM]`. |
| **2. Solo Dominio (`uc-only`)** | `domain-only` | `[]` (vacio) | 1 o mas `UC-*.md` existentes | Procesos internos sin cambios en pantalla ni interaccion nueva: migraciones SQLite *on-startup*, workers de indexacion en segundo plano, compactacion WAL, watchers de archivos o suscripciones entre modulos en el Event Bus. |
| **3. Solo Interfaz (`uf-only`)** | `ui-only` | 1 o mas `UF-*.md` existentes | `[]` (vacio) | Flujos puramente presentacionales, de navegacion o ergonomia sin reglas de negocio ni mutacion de entidades de dominio: cambio de tema (`light`/`dark`/`system`/`high-contrast`), modo de densidad, redimensionado/docking de paneles, dialogo "Acerca de" o paleta visual de comandos. El `UF-*` declara `invokes_use_case: N/A`. |

> **Nota sobre `PATCH` (*Fast-Track*) y `packaging-infra`:** Un requerimiento `PATCH` (correccion puntual sin alterar contratos funcionales ni de negocio) o `packaging-infra` (exclusivamente CI, instaladores, *Code Signing*) puede referenciar los documentos existentes afectados o declarar listas vacias si no modifica ningun contrato funcional.

---

## 3. Que Va y Que Esta Prohibido en Cada Documento

| Dimension | En `UF-*.md` (Capa de Presentacion) | En `UC-*.md` (Capa de Aplicacion y Dominio) |
| :--- | :--- | :--- |
| **Identificador y ubicacion** | `UF-[MODULO]-[NUM]` en `docs/functional/user-flows/` | `UC-[MODULO]-[NUM]` en `docs/functional/use-cases/` |
| **Contenido obligatorio y permitido** | - Ventana o dialogo destino (`window_target`) y geometria minima (`window_geometry`).<br>- Disparador de entrada (`entry_trigger`) y atajo de teclado (`shortcut`).<br>- Entradas del usuario (`user_inputs`) y validacion sintactica inmediata en campo (vacio, longitud, mascara).<br>- Salidas visuales (`visual_outputs`) y matriz de estados UI (`ui_states`: `Idle`, `Loading`/`Busy`, `Empty`, `Error`, `Dirty`).<br>- Diagrama Mermaid de flujo/FSM (`stateDiagram-v2` si `fsm_required: true`) e invariantes UI (`NoDoubleSubmit`, `PreserveDraftOnError`, `FocusRestoration`, `RollbackOnOptimisticFailure`, `NoMainThreadBlock`, `GuardUnsavedChangesOnClose`).<br>- Accesibilidad nativa (`focus_management`, `os_accessibility_roles`, `keyboard_navigation`).<br>- Delegacion explicita: `invokes_use_case: UC-XXX-NNN` (o `N/A`). | - Modulo dueno (`module`), actor invocador (`actor`) y disparador de aplicacion/evento (`trigger`).<br>- Precondiciones de dominio.<br>- Diagrama Mermaid de flujo de negocio o secuencia entre fachadas.<br>- Contratos DTO de `inputs` y `outputs` agnosticos de UI.<br>- Reglas de negocio `[BR-XX]` con contratos OCL (`pre`, `post` con `@pre`, `inv`) cuando aplica.<br>- Efectos secundarios (`side_effects`): `local_database`, `local_files`, `os_keyring`, `internal_domain_events`.<br>- Excepciones tipadas de dominio (`[EX-XX]`) que el ViewModel traducira a UI. |
| **Contenido ESTRICTAMENTE PROHIBIDO** | - Formulas de negocio, impuestos, descuentos o transiciones de entidad.<br>- Invariantes OCL de entidades de dominio (`context Account inv ...`).<br>- Nombres de tablas SQLite, sentencias SQL, `PRAGMA` o rutas de repositorios.<br>- Llamadas o nombres de clases de infraestructura (`SqliteConnection`, `KeyringService`).<br>- Rutas web (`^/`), viewports `mobile`/`tablet`, CSS/DOM o codigos HTTP. | - Nombres de ventanas, dialogos modales, botones, menues, tooltips o iconos.<br>- Tokens visuales, colores hex, skeletons, spinners o barras de progreso.<br>- Atajos de teclado (`Ctrl+S`), orden de tabulacion o foco.<br>- Nombres de `ViewModel`, `Presenter`, `Window`, widgets WPF/Avalonia/Qt/Compose/Slint.<br>- Descripciones de UI como "mostrar toast rojo" o "abrir MessageBox".<br>- Endpoints HTTP/REST, webhooks o codigos de estado web (`422`, `500`). |

### Regla de Traduccion de Errores en la Frontera

1. El `UC-*` evalua las reglas `[BR-XX]` y, ante incumplimiento, aborta retornando o lanzando una **excepcion/error tipado de dominio** (ej. `DuplicateSkuError`, `CorruptArchiveError`, `InsufficientBalanceError`).
2. El `UF-*` captura ese error tipado en el `ViewModel` / `Presenter` / `StateHolder` y define como se presenta al usuario (mensaje inline junto al campo, banner en barra superior, dialogo modal con opcion de reintento), preservando el borrador (`PreserveDraftOnError`) y manteniendo la ventana responsiva (`NoMainThreadBlock`).

---

## 4. Ejemplos de Especificacion Correcta vs. Antipatrones

### Ejemplo Correcto A — Escenario Dual (`UF -> UC`)

**En `UF-CATALOG-001.md`:**
```yaml
---
id: UF-CATALOG-001
title: "Registrar nuevo producto desde dialogo de editor"
module: catalog
actor: "Operador Local"
window_target: "ProductEditorDialog"
entry_trigger: "Menu Catalogo -> Nuevo producto o atajo Ctrl+N / Cmd+N"
status: Activo
invokes_use_case: UC-CATALOG-001
shortcut: "Ctrl+N / Cmd+N"
fsm_required: true
window_geometry:
  min_width_px: 520
  min_height_px: 420
  resizable: true
---
```
- Valida en el formulario que `sku` y `name` no esten vacios antes de habilitar el comando Guardar.
- Si el usuario pulsa `Guardar`, entra en estado `Busy` (`NoDoubleSubmit`), ejecuta `UC-CATALOG-001` en background worker (`NoMainThreadBlock`), y ante `DuplicateSkuError` preserva los campos (`PreserveDraftOnError`) y muestra error inline sobre el input `SKU` moviendo el foco hacia el.
- Si hay cambios sin guardar y el usuario pulsa `Escape` o `X`, solicita confirmacion (`GuardUnsavedChangesOnClose`) y al cerrar devuelve el foco al boton disparador en `MainWindow` (`FocusRestoration`).

**En `UC-CATALOG-001.md`:**
```yaml
---
id: UC-CATALOG-001
title: "Crear producto en el catalogo local"
module: catalog
actor: "Operador Local"
status: Activo
ocl_applied: true
trigger: "Comando CreateProductCommand invocado desde fachada del modulo catalog"
---
```
- Define `inputs`: `sku (String)`, `name (String)`, `unitPrice (Decimal)`.
- Define `[BR-01]` con OCL: `unitPrice > 0` y `not self.catalogRepository.existsBySku(input.sku)`.
- Define `side_effects.local_database`: `INSERT INTO catalog_products (id, sku, name, unit_price_cents)`.
- Define `side_effects.internal_domain_events`: `CatalogProductCreated(productId, sku)`.
- Define `[EX-01] DuplicateSkuError`: aborta sin escribir en SQLite ni emitir evento.

---

### Ejemplo Correcto B — `uc-only`

- **`UC-STORAGE-002.md`:** *"Ejecutar respaldo preventivo y migraciones SQLite WAL al arranque"*
  - `actor: "StartupBootstrapWorker"`, `trigger: "Evento interno AppInitialized antes de habilitar escritura en modulos"`.
  - No existe `UF-*` porque no requiere ventana ni interaccion; si falla `[EX-01] IncompatibleSchemaVersionError`, la capa de arranque del host mostrara un dialogo de error fatal segun `windowing-and-os-contracts.md`.

---

### Ejemplo Correcto C — `uf-only`

- **`UF-SHELL-003.md`:** *"Alternar tema claro/oscuro/sistema y densidad de paneles en ventana principal"*
  - `invokes_use_case: N/A`, `shortcut: "Ctrl+Shift+D / Cmd+Shift+D"`.
  - Persiste preferencia local de UI sin reglas de negocio de dominio ni entidades OCL.

---

### Antipatrones Prohibidos (Que Rechazar en Revisiones y `dspec check`)

1. **Antipatron 1 — Contaminacion UI dentro de `UC-*`:**
   - *Incorrecto:* "El caso de uso `UC-INVOICE-001` escucha el clic en `btnEmitir`, deshabilita el boton, consulta `SELECT * FROM invoices`, y si falla muestra un `MessageBox` rojo."
   - *Por que falla:* Mezcla eventos de boton, bloqueo visual de controles y `MessageBox` dentro de la capa de dominio.
   - *Correccion:* Dejar clic, deshabilitado (`NoDoubleSubmit`) y dialogo visual en `UF-INVOICE-001` (`invokes_use_case: UC-INVOICE-001`), y dejar en `UC-INVOICE-001` solo el comando DTO, las reglas `[BR-XX]` OCL, la escritura SQLite y la excepcion tipada.

2. **Antipatron 2 — Reglas de negocio o SQL dentro de `UF-*`:**
   - *Incorrecto:* "En `UF-INVOICE-001`, calcular `total = subtotal * 1.16` segun `[BR-02]`, validar en SQLite que `stock >= qty` y actualizar la tabla `inventory_items`."
   - *Por que falla:* Rompe la modularidad y duplica o esconde invariantes de dominio dentro de un `ViewModel` o vista.
   - *Correccion:* El `UF-*` solo captura el valor numerico positivo en la caja de texto y delega calculo, validacion de stock y actualizacion de tablas al `UC-*`.

3. **Antipatron 3 — Duplicacion especular o `UC-*` vacio:**
   - *Incorrecto:* Crear `UC-ABOUT-001` ("Mostrar informacion de version de la aplicacion") sin reglas `[BR-*]` ni persistencia solo para acompaniar a `UF-ABOUT-001`, o copiar palabra por palabra las mismas tablas en `UF-*` y `UC-*`.
   - *Por que falla:* Introduce burocracia sin valor arquitectonico.
   - *Correccion:* Usar `uf-only` (`invokes_use_case: N/A`) cuando no hay dominio real.

4. **Antipatron 4 — Contaminacion Web / HTTP:**
   - *Incorrecto:* Declarar `route: "/catalog/new"`, `viewports: [mobile, desktop]`, `HTTP 422 Unprocessable Entity` o `POST /api/v1/products` en un `UF-*` o `UC-*`.
   - *Por que falla:* `desktop-spec` v1.0 gobierna monolitos nativos standalone sin servidor HTTP propio ni navegacion por URL web.

---

## 5. Checklist Rapido Antes de Cerrar Especificaciones

- [ ] Todo `UF-*` tiene `window_target`, `entry_trigger`, `accessibility` nativa y `invokes_use_case` (`UC-*` existente o `N/A`).
- [ ] Ningun `UF-*` contiene sentencias SQL, nombres de tablas, formulas de dominio ni contratos OCL de entidades.
- [ ] Ningun `UC-*` menciona ventanas, dialogos, botones, atajos de teclado, colores ni protocolos HTTP de servidor.
- [ ] Todo `REQ-DESK-*` `MAJOR`/`MINOR` cumple exactamente uno de los 3 escenarios (`dual UF->UC`, `uc-only`, `uf-only`).
