# Plantilla Spec-First: Pruebas de Dominio, Persistencia Local y Fronteras Modulares

> **Proposito:** Estandarizar la generacion de pruebas en estado inicial rojo (`RED`) antes de implementar la logica de negocio o persistencia de un caso de uso `UC-*`, o al reproducir un defecto en modo *Fast-Track (`PATCH`)*.
> Toda prueba debe incluir trazabilidad explicita con `@spec`, `@req` e `@invariant` (o regla `[BR-XX]`), ejecutarse sin red ni servidor externo y aislar SQLite o archivos en memoria/directorios temporales.

---

## 1. C# (.NET 8+ / `xUnit`)

```csharp
using System;
using Xunit;

namespace App.Modules.Catalog.Tests;

/// <summary>
/// @spec UC-CATALOG-001
/// @req REQ-DESK-CATALOG-001
/// </summary>
public sealed class CreateProductUseCaseTests
{
    [Fact]
    public void Execute_WhenInputsValid_PersistsLocallyAndEmitsDomainEvent()
    {
        // Arrange: repositorio SQLite en memoria y Event Bus interno de pruebas
        // Act & Assert
        Assert.Fail("Estado inicial RED: implementar CreateProductUseCase");
    }

    /// <summary>
    /// @invariant BR-01
    /// </summary>
    [Fact]
    public void Execute_WhenSkuDuplicated_ThrowsDomainRuleExceptionWithoutSideEffects()
    {
        // Verificar precondicion OCL BR-01 y ausencia de escritura en SQLite / Event Bus
        Assert.Fail("Estado inicial RED: validar invariante BR-01");
    }
}
```

---

## 2. Python (`pytest` + `sqlite3` / `tmp_path`)

```python
import pytest


# @spec UC-LEDGER-002
# @req REQ-DESK-LEDGER-001
class TestTransferLocalFundsUseCase:
    def test_valid_transfer_updates_balances_and_emits_event(self, tmp_path):
        # Usar tmp_path / sqlite3(":memory:") aislado por prueba
        pytest.fail("Estado inicial RED: implementar TransferLocalFundsUseCase")

    # @invariant BR-01
    def test_rejects_non_positive_amount_preserving_balances(self, tmp_path):
        pytest.fail("Estado inicial RED: validar precondicion OCL BR-01")

    # @invariant INV-02
    def test_locked_account_rejects_mutation(self, tmp_path):
        pytest.fail("Estado inicial RED: validar invariante INV-02")
```

---

## 3. Kotlin (JVM / `JUnit 5`)

```kotlin
package app.modules.project

import org.junit.jupiter.api.Assertions.fail
import org.junit.jupiter.api.Tag
import org.junit.jupiter.api.Test

/**
 * @spec UC-PROJECT-003
 * @req REQ-DESK-PROJECT-001
 */
class AddAttachmentUseCaseTest {

    @Test
    fun `persists attachment metadata in local database and updates quota`() {
        fail<Unit>("Estado inicial RED: implementar AddAttachmentUseCase")
    }

    /**
     * @invariant BR-01
     */
    @Test
    @Tag("invariant")
    fun `rejects attachment when quota exceeded without mutating archive`() {
        fail<Unit>("Estado inicial RED: validar invariante de cuota BR-01")
    }
}
```

---

## 4. Rust (`cargo test`)

```rust
// @spec UC-VAULT-004
// @req REQ-DESK-VAULT-001
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rotate_master_key_updates_local_keyring_and_version() {
        todo!("Estado inicial RED: implementar rotate_master_key");
    }

    // @invariant BR-01
    #[test]
    fn rotate_master_key_rejects_locked_session() {
        // Verificar precondicion SessionUnlocked y ausencia de cambios en Keyring/SQLite
        todo!("Estado inicial RED: validar invariante SessionUnlocked");
    }
}
```

---

## 5. Verificacion de Fronteras del Monolito Modular

Complementar las pruebas de dominio con una verificacion automatica de imports/dependencias entre modulos:
- Ningun modulo `A` puede importar clases internas, tablas SQLite o repositorios de un modulo `B`; solo puede invocar la fachada o puerto publico de `B` o suscribirse al Event Bus interno.
- La capa de dominio (`UC-*`) nunca debe importar namespaces o paquetes de UI (`Avalonia`, `System.Windows`, `PySide6`, `androidx.compose`, `slint`).
