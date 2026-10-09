# ARCHITECTURE RULES — Reglas de Arquitectura y Desarrollo LEAF ERP

Este documento consolida las directrices técnicas, restricciones y estándares arquitectónicos vigentes en el desarrollo de **LEAF ERP** sobre **ERPNext y Frappe**.

---

## 1. Filosofía "ERPNext como Motor" y Principio de Zero-Fork Preferente

- **LEAF como Orquestador**: LEAF añade la lógica comercial, procesos operativos específicos y flujos de usuario.
- **ERPNext como Motor Transaccional**: ERPNext es la autoridad y ejecutor de la contabilidad (`GL Entry`), inventario (`Stock Ledger Entry`), pagos (`Payment Entry`), cuentas por cobrar/pagar y cálculo de impuestos.
- **Prohibición de Motores Paralelos**: Queda estrictamente prohibido construir motores de cálculo o tablas contables que sustituyan o dupliquen el módulo de Cuentas o Inventario de ERPNext.

---

## 2. Jerarquía de Riesgo en Upgrades (Escala A ➔ E)

Todo diseño técnico debe ubicarse en la categoría más baja posible de la siguiente escala:

| Categoría | Nivel de Extensión | Riesgo de Upgrade | Descripción |
| :--- | :--- | :--- | :--- |
| **Categoría A** | Estándar ERPNext | **Cero** | Reutilización directa de DocTypes, APIs y flujos nativos sin código personalizado. |
| **Categoría B** | Configuración Declarativa | **Muy Bajo** | Custom Fields, Property Setters, Client Scripts, Workflows, Print Formats y Reports. |
| **Categoría C** | Custom App LEAF | **Controlado** | Código encapsulado dentro de la app `leaf`, extendiendo vía hooks (`doc_events`) o nuevos DocTypes no existentes. |
| **Categoría D** | Override Controlado | **Alto** | Sobrescritura de métodos (`override_whitelisted_methods`, `override_doctype_class`). Requiere justificación técnica. |
| **Categoría E** | Modificación Core (Fork) | **Extremo (Último Recurso)** | Cambio en el código fuente de repositorios base (`frappe` / `erpnext`). Requiere aprobación especial. |

---

## 3. Reglas de Desarrollo Backend (Python / Frappe)

1. **Reutilización de APIs Nativas**: Antes de escribir un método, reutilizar APIs estándar (`make_sales_invoice`, `get_payment_entry`, `calculate_taxes_and_totals`).
2. **Atomicidad y Manejo de Transacciones**: Usar transacciones seguras de base de datos.
3. **Respeto a `docstatus`**: Toda lógica transaccional debe validar el estado del documento:
   - `docstatus = 0`: Borrador (Draft).
   - `docstatus = 1`: Enviado / Sometido (Submitted).
   - `docstatus = 2`: Cancelado (Cancelled).
4. **Reversibilidad Obligatoria**: Toda acción que modifique acumuladores o genere documentos en `on_submit` DEBE implementar su contraparte limpia de reversión en `on_cancel` o `on_trash`.
5. **No Creación Manual de Asientos**: NUNCA insertar registros directos en `tabGL Entry` o `tabStock Ledger Entry` mediante SQL manual si un documento transaccional estándar puede generarlos.

---

## 4. Reglas de Desarrollo Frontend (JavaScript / Desk)

1. **Capa de UX, No Fuente de Verdad**: El JavaScript del Desk (`frm.*`) es exclusivamente para asistencia visual, validaciones de entrada, filtros de campos (`set_query`) y mejorar la experiencia de usuario.
2. **Prohibición de Cálculos Críticos en JS**: Ninguna fórmula fiscal, impuesto, saldo contable o validación de seguridad debe existir únicamente en el cliente. El backend es la única fuente de verdad.
3. **Consumo de Endpoints**: Consumir los resultados del servidor mediante `frappe.call` o eventos de formulario (`frm.refresh_field`) en lugar de recalcular en el navegador.
4. **Uso de APIs Nativas del Formulario**: Emplear `frm.set_value()`, `frm.set_df_property()`, `frm.toggle_display()`, `frm.toggle_reqd()` y `frm.add_custom_button()`. Evitar manipulación directa del DOM con jQuery salvo imposibilidad técnica.

---

## 5. Reglas de Integridad de Datos y Migraciones

1. **Premisa de Datos Reales**: Nunca asumir bases de datos vacías. Toda modificación opera sobre registros históricos en producción.
2. **Preservación de Documentos Congelados**: Los documentos históricos sometidos (`docstatus = 1`) no deben alterarse retroactivamente a menos que exista una instrucción explícita de saneamiento.
3. **Idempotencia en Parches**: Todo script en `patches.txt` debe ser idempotente (capaz de ejecutarse múltiples veces con el mismo resultado).
4. **Procesamiento en Lotes (`Batching`)**: Para grandes volúmenes de datos históricos, realizar operaciones en lotes con límites de paginación para evitar desbordamiento de memoria.
5. **Separación Esquema vs Datos**: Separar la migración estructural de DocTypes de la manipulación o recálculo de datos.

---

## 6. Reglas de Pruebas y Aseguramiento de Calidad (QA)

1. **7 Dimensiones de Cobertura Obligatorias**:
   - **Dimensión A**: Comportamiento Estándar ERPNext.
   - **Dimensión B**: Funcionalidad LEAF.
   - **Dimensión C**: Integración LEAF ➔ ERPNext.
   - **Dimensión D**: Regresión en módulos adyacentes.
   - **Dimensión E**: Datos Existentes e Históricos (Draft, Submit, Cancel).
   - **Dimensión F**: Casos Negativos y Escenarios Borde.
   - **Dimensión G**: Flujo Completo End-to-End.
2. **Clasificación Estricta de Estados de Evidencia**:
   - `VERIFIED`: Ejecutado y comprobado activamente con comandos o logs.
   - `ANALYZED`: Inspeccionado estáticamente en código.
   - `PROPOSED`: Planificado o diseñado pendiente de ejecución.
   - `BLOCKED`: Impedido por limitaciones del entorno.

---

## 7. Reglas de Higiene en Git y Repositorios

1. **DocType JSON Versionado**: Todo cambio en campos o configuración de DocType debe incluir la actualización de su respectivo archivo `.json`.
2. **Commits Atómicos**: No mezclar refactorizaciones generales con correcciones de bugs o nuevas funcionalidades en un mismo commit.
3. **Diffs Limpios**: Sin espacios en blanco al final de línea, sin caracteres de control extraños y sin rutas absolutas locales.
4. **Protección de Historial**: Prohibido eliminar o sobrescribir código previo sin análisis previo de trazabilidad en Git.

---

## 8. Reglas de Infraestructura y Seguridad (Docker & Supply Chain)

1. **Fijación de Versiones**: Evitar tags flotantes (`latest`) en dependencias e imágenes de producción; fijar versiones exactas o hashes SHA.
2. **Protección de Secretos**: Prohibido incluir credenciales, llaves API o contraseñas en archivos versionados, Dockerfiles, Compose o logs.
3. **Mínimo Privilegio**: Configurar ejecución con usuarios no-root en contenedores y permisos mínimos en GitHub Actions.
