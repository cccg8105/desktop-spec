# Plantilla Spec-First: Pruebas de Interaccion UI Nativa, FSM y Accesibilidad OS

> **Proposito:** Estandarizar la verificacion automatizada de flujos `UF-*`, contratos `ocl-ui` (`NoDoubleSubmit`, `PreserveDraftOnError`, `FocusRestoration`, `RollbackOnOptimisticFailure`, `NoMainThreadBlock`, `GuardUnsavedChangesOnClose`) y accesibilidad nativa del sistema operativo.
> Todo test UI se ejecuta contra el adapter headless o de automatizacion del toolkit nativo, simulando el puerto `UC-*` con un doble determinista.

---

## 1. Lista de Verificacion por Flujo (`UF-*`)

1. **Trazabilidad:** Declarar `@spec UF-[MODULO]-[NUM]`, `@req REQ-DESK-[MODULO]-[NUM]` e `@invariant` en cada prueba de contrato UI.
2. **Invariantes `ocl-ui`:** Verificar `NoDoubleSubmit`, `PreserveDraftOnError`, `NoMainThreadBlock` (< 16ms en UI Thread), `FocusRestoration` y `GuardUnsavedChangesOnClose`.
3. **Accesibilidad Nativa:** Comprobar nombre/rol accesible del SO (`AutomationProperties.Name`, `accessibleName`, `contentDescription`) y navegacion completa por teclado (`Tab`, `Enter`, `Escape`).

---

## 2. C# (.NET / `xUnit` + `Avalonia.Headless` / `FlaUI`)

```csharp
using System.Threading.Tasks;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Xunit;

namespace App.UI.Tests;

/// <summary>
/// @spec UF-CATALOG-001
/// @req REQ-DESK-CATALOG-001
/// </summary>
public sealed class ProductEditorDialogTests
{
    /// <summary>
    /// @invariant NoDoubleSubmit
    /// @invariant NoMainThreadBlock
    /// </summary>
    [AvaloniaFact]
    public void SaveCommand_DisablesResubmitWhileWorkerPending()
    {
        // Arrange: ViewModel con doble de UC-CATALOG-001 bloqueado via TaskCompletionSource
        // Act: pulsar Guardar / Ctrl+S dos veces mientras IsBusy == true
        // Assert: SaveCommand.CanExecute(null) == false y useCaseInvocations == 1
        Assert.Fail("Estado inicial RED: implementar ProductEditorDialog y ViewModel");
    }

    /// <summary>
    /// @invariant PreserveDraftOnError
    /// @invariant GuardUnsavedChangesOnClose
    /// </summary>
    [AvaloniaFact]
    public void ClosingDirtyDialog_PromptsConfirmationAndPreservesDraftOnCancel()
    {
        // Nota para Windows UI Automation (WPF/WinUI 3 con FlaUI):
        // Usar AutomationElement.FindFirstDescendant(...) y comprobar HasKeyboardFocus + Name.
        Assert.Fail("Estado inicial RED: validar dialogo de cambios sin guardar");
    }
}
```

---

## 3. Python (`pytest` + `pytest-qt`)

```python
import pytest
from PySide6.QtCore import Qt


# @spec UF-CATALOG-001
# @req REQ-DESK-CATALOG-001
class TestProductEditorDialog:
    # @invariant NoDoubleSubmit
    # @invariant NoMainThreadBlock
    def test_prevents_double_submit_while_worker_busy(self, qtbot):
        # Arrange: dialog con worker en QThreadPool controlado y spy de UC-CATALOG-001
        # Act: qtbot.mouseClick(save_btn, Qt.LeftButton) x2
        # Assert: not save_btn.isEnabled() y spy_calls == 1
        pytest.fail("Estado inicial RED: implementar ProductEditorDialog")

    # @invariant PreserveDraftOnError
    # @invariant FocusRestoration
    def test_preserves_draft_on_domain_error_and_restores_focus_on_escape(self, qtbot):
        # Verificar accessibleName no vacio y qtbot.keyClick(dialog, Qt.Key_Escape)
        pytest.fail("Estado inicial RED: validar PreserveDraftOnError y FocusRestoration")
```

---

## 4. Kotlin (JVM / `JUnit 5` + `Compose UI Test`)

```kotlin
package app.ui.catalog

import androidx.compose.ui.input.key.Key
import androidx.compose.ui.test.*
import org.junit.jupiter.api.Assertions.fail
import org.junit.jupiter.api.Test

/**
 * @spec UF-CATALOG-001
 * @req REQ-DESK-CATALOG-001
 */
class ProductEditorDialogTest {

    /**
     * @invariant NoDoubleSubmit
     * @invariant NoMainThreadBlock
     */
    @OptIn(ExperimentalTestApi::class)
    @Test
    fun saveButtonDisablesDuringSubmitAndExecutesUseCaseOnce() = runComposeUiTest {
        // Verificar onNodeWithTag("saveBtn").assertIsNotEnabled() tras primer clic
        // y onNodeWithContentDescription("Guardar producto").assertExists()
        fail<Unit>("Estado inicial RED: implementar ProductEditorDialog en Compose")
    }

    /**
     * @invariant PreserveDraftOnError
     * @invariant GuardUnsavedChangesOnClose
     */
    @Test
    fun escapeOnDirtyEditorShowsUnsavedChangesDialogAndPreservesInput() = runComposeUiTest {
        fail<Unit>("Estado inicial RED: validar GuardUnsavedChangesOnClose")
    }
}
```

---

## 5. Rust (`cargo test` con adaptador headless Slint / UI)

```rust
// @spec UF-CATALOG-001
// @req REQ-DESK-CATALOG-001
#[cfg(test)]
mod ui_tests {
    // @invariant NoDoubleSubmit
    // @invariant PreserveDraftOnError
    #[test]
    fn editor_blocks_double_submit_and_preserves_draft_on_error() {
        // En Slint: usar slint_testing::init_no_event_loop() y simular invocaciones
        // sobre propiedades reactivas y callbacks hacia el puerto de dominio.
        todo!("Estado inicial RED: implementar estado FSM de ProductEditor");
    }

    // @invariant GuardUnsavedChangesOnClose
    #[test]
    fn dirty_editor_requests_confirmation_before_closing() {
        todo!("Estado inicial RED: validar guarda de cierre sin guardar");
    }
}
```
