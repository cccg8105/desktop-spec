# Molde de Referencia: Propuesta de Auditoria y Deuda Tecnica Desktop
*Este documento reside en `.spec/templates/_template_audit_proposals.md` como blueprint del agente.*

```markdown
### [AUDIT-DESK-[DOMINIO]-[NUMERO]] [Titulo conciso del hallazgo desktop]
- **Dominio:** `[dominio]`
- **Categoria:** [Frontera Modular | Bloqueo Hilo UI | Persistencia / Migracion | Seguridad Local | Accesibilidad Nativa | Doc Drift | Brecha de Tests | Codigo Muerto]
- **Severidad Sugerida:** [P1 (Critica) | P2 (Media) | P3 (Baja)]
- **Impacto Estimado:** [MAJOR | MINOR | PATCH]
- **Evidencia en Codigo:** `[ruta/al/archivo.ext:L10-L25]`
- **Estado:** [Propuesto | Promovido a REQ-DESK-... | Descartado]

#### Descripcion del Hallazgo:
[Explicacion objetiva fundamentada en codigo, logs o tests. ¿Que modulo rompe fronteras de fachada, bloquea el hilo UI, omite OS Keyring, viola invariantes de ventana o presenta desfase documental?]

#### Propuesta de Remediacion:
[Recomendacion concisa de como resolverlo al promoverlo formalmente a docs/backlog/pending.md mediante desktop-spec req:new --from-audit.]
```
