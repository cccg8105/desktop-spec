# Guia y Estandar de OCL (Object Constraint Language) para `desktop-spec`

Este documento define el subconjunto practico de **Object Constraint Language (OCL)** adoptado por `desktop-spec` para eliminar la ambiguedad en reglas de negocio, precondiciones, postcondiciones e invariantes de entidades dentro de **monolitos modulares desktop nativos** (C#/.NET, Python, Kotlin y Rust), sin dependencias HTTP ni de servidor remoto.

---

## 1. Alcance y Frontera Dentro del Monolito Modular

- **Donde se usa OCL de dominio (`ocl`):** Exclusivamente en especificaciones de casos de uso (`docs/functional/use-cases/UC-*.md`) y en entidades/agregados de dominio de `docs/technical/modular-architecture.md`.
- **Donde NO se usa OCL de dominio:** Nunca en flujos de interfaz (`UF-*`), ventanas, `ViewModels` o widgets. Los contratos de interfaz usan el dialecto `ocl-ui` documentado en `ui-contracts-guidelines.md`.
- **Cero contaminacion web:** Todas las operaciones OCL se ejecutan en memoria dentro del proceso nativo sobre puertos/repositorios locales (SQLite/WAL, archivos de proyecto, *OS Keyring*) y publican eventos en el Event Bus interno del monolito.
- **Heuristica de aplicacion (`ocl_applied`):**
  - **Obligatorio (`ocl_applied: true`):** Calculos financieros o tecnicos de precision (`Decimal`), maquinas de estado de entidades o documentos (`Draft -> Locked -> Archived`), restricciones multi-campo, validaciones de saldo/cuota o invariantes que cruzan colecciones.
  - **Opcional (`ocl_applied: false`):** Consultas de solo lectura sin filtros complejos o altas simples con validaciones unitarias triviales de tipo/longitud.

---

## 2. Subconjunto de Sintaxis Autorizado

| Elemento OCL | Ambito | Significado y Traduccion a Codigo Nativo |
| :--- | :--- | :--- |
| `context [Tipo]::[operacion]` | Caso de uso / Servicio | Ambito del comando o metodo publico de la fachada del modulo. |
| `pre [Nombre]: [expresion]` | Precondicion | Condicion que **DEBE** cumplirse antes de mutar estado. Se traduce a clausulas de guarda que lanzan/retornan una excepcion tipada de dominio (`DomainError`, `Err(...)`). |
| `post [Nombre]: [expresion]` | Postcondicion | Estado que **DEBE** garantizarse al finalizar la operacion (incluyendo eventos internos emitidos). Se traduce a aserciones en pruebas unitarias de dominio. |
| `inv [Nombre]: [expresion]` | Invariante de entidad | Condicion permanente de una entidad o agregado. Se valida en constructor, fabricas y metodos mutadores. |
| `@pre` | Expresion | Valor de un atributo o coleccion antes de iniciar la operacion (ej. `self.balance = self.balance@pre - amount`). |
| `implies` | Logica | Implicacion booleana (`A implies B`: si A es verdadero, B debe ser verdadero). |
| `self` | Instancia | Referencia a la entidad o servicio propietario del contexto actual. |
| `->forAll(x \| ...)` | Colecciones | Garantiza que todos los elementos de la coleccion cumplen el predicado. |
| `->exists(x \| ...)` | Colecciones | Garantiza que al menos un elemento cumple el predicado. |
| `->size()` / `->select(...)` | Colecciones | Conteo o filtrado declarativo sobre lineas, items o adjuntos locales. |

### Regla de Frontera Entre Modulos del Monolito

Si una precondicion de un `UC-*` del modulo `A` necesita verificar un estado perteneciente al modulo `B`, el contrato OCL invoca exclusivamente la **fachada o puerto de consulta publico** del modulo `B` (ej. `self.catalogPort.isSkuActive(sku)`), nunca tablas SQLite ni entidades privadas de `B`. Los efectos secundarios en `B` se expresan mediante eventos internos en `side_effects.internal_domain_events`.

---

## 3. Ejemplos Practicos de Traduccion Multi-Ecosistema

### A. C# (.NET 8+ / WPF, WinUI 3, Avalonia, MAUI Desktop) + xUnit

#### Especificacion OCL en `UC-BILLING-001.md`:
```ocl
context IssueLocalInvoiceUseCase::execute(invoice: LocalInvoice, customerActive: Boolean)
pre InvoiceInDraft:
    invoice.status = InvoiceStatus::DRAFT
pre CustomerIsActive:
    customerActive = true
pre HasValidLines:
    invoice.lines->size() > 0 and invoice.lines->forAll(l | l.quantity > 0 and l.unitPrice >= 0)
post StatusFinalized:
    invoice.status = InvoiceStatus::FINALIZED
post TotalMatchesLines:
    invoice.totalAmount = invoice.lines->collect(l | l.quantity * l.unitPrice)->sum()
```

#### Traduccion en Dominio y Aplicacion (`src/Modules/Billing/`):
```csharp
public sealed class LocalInvoice
{
    private readonly List<InvoiceLine> _lines = new();
    public InvoiceStatus Status { get; private set; } = InvoiceStatus.Draft;
    public decimal TotalAmount { get; private set; }
    public IReadOnlyList<InvoiceLine> Lines => _lines;

    public void FinalizeInvoice(bool customerActive)
    {
        if (Status != InvoiceStatus.Draft)
            throw new DomainRuleException("BR-01", "Solo las facturas en borrador pueden finalizarse.");
        if (!customerActive)
            throw new DomainRuleException("BR-02", "El cliente local esta inactivo.");
        if (_lines.Count == 0 || _lines.Any(l => l.Quantity <= 0 || l.UnitPrice < 0m))
            throw new DomainRuleException("BR-03", "La factura requiere al menos una linea valida.");

        TotalAmount = _lines.Sum(l => l.Quantity * l.UnitPrice);
        Status = InvoiceStatus.Finalized;
    }
}
```

#### Prueba Unitaria de Postcondiciones (`tests/Billing.Tests/`):
```csharp
[Fact]
public void FinalizeInvoice_SatisfiesStatusAndTotalPostconditions()
{
    var invoice = new LocalInvoice();
    invoice.AddLine("SKU-01", quantity: 2, unitPrice: 15.50m);

    invoice.FinalizeInvoice(customerActive: true);

    Assert.Equal(InvoiceStatus.Finalized, invoice.Status);
    Assert.Equal(31.00m, invoice.TotalAmount);
}
```

---

### B. Python (PySide6, PyQt6, Flet) + pytest

#### Especificacion OCL en `UC-LEDGER-002.md`:
```ocl
context WalletAccount::transferTo(target: WalletAccount, amount: Decimal)
pre PositiveAmount:
    amount > 0
pre DistinctAccounts:
    self.id <> target.id
pre SufficientBalance:
    self.balance >= amount
inv NonNegativeBalance:
    self.balance >= 0
inv LockedAccountImmutable:
    self.isLocked implies self.balance = self.balance@pre
post BalancesConserved:
    self.balance = self.balance@pre - amount and target.balance = target.balance@pre + amount
```

#### Traduccion en Dominio (`src/modules/ledger/domain.py`):
```python
from dataclasses import dataclass
from decimal import Decimal


class DomainRuleError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass
class WalletAccount:
    id: str
    balance: Decimal
    is_locked: bool = False

    def __post_init__(self) -> None:
        self._validate_invariants()

    def _validate_invariants(self) -> None:
        if self.balance < Decimal("0"):
            raise DomainRuleError("INV-01", "El saldo de la cuenta no puede ser negativo.")

    def transfer_to(self, target: "WalletAccount", amount: Decimal) -> None:
        if amount <= Decimal("0"):
            raise DomainRuleError("BR-01", "El monto debe ser mayor que cero.")
        if self.id == target.id:
            raise DomainRuleError("BR-02", "Origen y destino deben ser distintos.")
        if self.is_locked or target.is_locked:
            raise DomainRuleError("INV-02", "Una cuenta bloqueada no admite movimientos.")
        if self.balance < amount:
            raise DomainRuleError("BR-03", "Saldo insuficiente para completar la transferencia local.")

        self.balance -= amount
        target.balance += amount
        self._validate_invariants()
        target._validate_invariants()
```

#### Prueba Unitaria (`tests/unit/test_ledger_domain.py`):
```python
from decimal import Decimal
import pytest
from modules.ledger.domain import DomainRuleError, WalletAccount


def test_transfer_conserves_balances_postcondition():
    src = WalletAccount(id="cash", balance=Decimal("100.00"))
    dst = WalletAccount(id="savings", balance=Decimal("25.00"))

    src.transfer_to(dst, Decimal("40.00"))

    assert src.balance == Decimal("60.00")
    assert dst.balance == Decimal("65.00")


def test_locked_account_rejects_mutation():
    src = WalletAccount(id="cash", balance=Decimal("100.00"), is_locked=True)
    dst = WalletAccount(id="savings", balance=Decimal("25.00"))

    with pytest.raises(DomainRuleError):
        src.transfer_to(dst, Decimal("10.00"))
    assert src.balance == Decimal("100.00")
```

---

### C. Kotlin (Compose Desktop / JavaFX) + JUnit 5

#### Especificacion OCL en `UC-PROJECT-003.md`:
```ocl
context ProjectArchive::addAttachment(fileSizeBytes: Long, maxQuotaBytes: Long)
pre PositiveFileSize:
    fileSizeBytes > 0
pre WithinQuota:
    self.usedBytes + fileSizeBytes <= maxQuotaBytes
inv UsageConsistent:
    self.usedBytes <= maxQuotaBytes
post UsageIncremented:
    self.usedBytes = self.usedBytes@pre + fileSizeBytes
```

#### Traduccion en Dominio (`modules/project/domain/ProjectArchive.kt`):
```kotlin
class QuotaExceededException(message: String) : IllegalStateException(message)

class ProjectArchive(
    private val maxQuotaBytes: Long,
    initialUsedBytes: Long = 0L
) {
    var usedBytes: Long = initialUsedBytes
        private set

    init {
        require(usedBytes in 0L..maxQuotaBytes) { "Uso inicial fuera de cuota permitida." }
    }

    fun addAttachment(fileSizeBytes: Long) {
        require(fileSizeBytes > 0L) { "El tamano del adjunto debe ser positivo." }
        if (usedBytes + fileSizeBytes > maxQuotaBytes) {
            throw QuotaExceededException("El adjunto supera la cuota local del proyecto.")
        }
        usedBytes += fileSizeBytes
    }
}
```

#### Prueba Unitaria (`modules/project/src/test/kotlin/ProjectArchiveTest.kt`):
```kotlin
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class ProjectArchiveTest {
    @Test
    fun `addAttachment increments usedBytes and enforces quota`() {
        val archive = ProjectArchive(maxQuotaBytes = 1024L, initialUsedBytes = 512L)
        archive.addAttachment(256L)
        assertEquals(768L, archive.usedBytes)

        assertThrows(QuotaExceededException::class.java) {
            archive.addAttachment(300L)
        }
        assertEquals(768L, archive.usedBytes)
    }
}
```

---

### D. Rust (`rust-native`: Slint / Iced / egui) + `cargo test`

#### Especificacion OCL en `UC-VAULT-004.md`:
```ocl
context VaultSession::rotateMasterKey(newKeyVersion: Int)
pre SessionUnlocked:
    self.isUnlocked = true
pre MonotonicVersion:
    newKeyVersion > self.keyVersion
inv LockedHasNoKeyMaterial:
    self.isUnlocked = false implies self.activeKeyId = null
post VersionUpdated:
    self.keyVersion = newKeyVersion and self.keyVersion > self.keyVersion@pre
```

#### Traduccion en Dominio (`src/modules/vault/domain.rs`):
```rust
#[derive(Debug, PartialEq, Eq)]
pub enum VaultError {
    SessionLocked,
    NonMonotonicKeyVersion,
}

pub struct VaultSession {
    is_unlocked: bool,
    key_version: u32,
    active_key_id: Option<String>,
}

impl VaultSession {
    pub fn new(is_unlocked: bool, key_version: u32, active_key_id: Option<String>) -> Self {
        assert!(is_unlocked || active_key_id.is_none(), "Invariante: sesion bloqueada sin clave en memoria");
        Self { is_unlocked, key_version, active_key_id }
    }

    pub fn rotate_master_key(&mut self, new_key_version: u32) -> Result<(), VaultError> {
        if !self.is_unlocked {
            return Err(VaultError::SessionLocked);
        }
        if new_key_version <= self.key_version {
            return Err(VaultError::NonMonotonicKeyVersion);
        }
        self.key_version = new_key_version;
        Ok(())
    }

    pub fn key_version(&self) -> u32 {
        self.key_version
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rotate_master_key_respects_pre_and_postconditions() {
        let mut session = VaultSession::new(true, 1, Some("keyring-slot-1".into()));
        assert_eq!(session.rotate_master_key(1), Err(VaultError::NonMonotonicKeyVersion));
        assert_eq!(session.rotate_master_key(2), Ok(()));
        assert_eq!(session.key_version(), 2);
    }
}
```
