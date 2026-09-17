# DOCUMENTACIÓN DE IMPLEMENTACIÓN: COMPARTIR SALES INVOICE (WHATSAPP + PDF PÚBLICO)

## 1. RESUMEN DE LA SOLUCIÓN

Se ha optimizado la funcionalidad de **Compartir Facturas de Venta (Sales Invoice)** para resolver dos necesidades clave:

1. **Corrección de Enlaces Rotos en WhatsApp**:
   - Anteriormente, el nombre del DocType (`Sales Invoice`) contenía un espacio en el query parameter de la URL (`doctype=Sales Invoice`). WhatsApp truncaba el hipervínculo en el espacio, dejando el resto como texto plano roto.
   - **Solución**: Los parámetros del enlace ahora se codifican correctamente (`urllib.parse.quote_plus` / `encodeURIComponent`), generando URLs continuas y 100% clickeables (ej. `doctype=Sales+Invoice`).

2. **Acceso Público para Clientes Sin Login (`allow_guest=True`)**:
   - Los clientes finales no tienen usuario ni contraseña en LEAF ERP. Al hacer clic en el enlace de WhatsApp, el sistema les solicitaba inicio de sesión.
   - **Solución Segura con Firma Criptográfica (`share_key`)**:
     - Cada factura genera una firma única basada en su identificador, fecha y secreto del sistema (`key=...`).
     - El endpoint `download_pdf` permite acceso público (`allow_guest=True`) validando la clave `key`.
     - El cliente final puede ver y descargar su PDF oficial con un solo toque desde WhatsApp **sin requerir inicio de sesión**.
     - Evita que terceros no autorizados puedan consultar facturas arbitrarias sin poseer el enlace firmado.

---

## 2. ARCHIVOS MODIFICADOS Y CREADOS

### A. Backend (`erpnext/accounts/doctype/sales_invoice/share_invoice.py`)
- `get_document_share_key(doc)`: Genera firma SHA256 única y segura por documento.
- `get_share_details(doctype, name, format=None, host=None)`:
  - Genera el mensaje con URL codificada y firma `key`.
- `download_pdf(doctype, name, format=None, no_letterhead=0, letterhead=None, key=None)`:
  - Whitelist con `allow_guest=True`.
  - Valida la firma del documento para clientes invitados (Guest) y permisos estándar para usuarios autenticados.

### B. Frontend (`erpnext/accounts/doctype/sales_invoice/sales_invoice.js`)
- Diálogo modal con integración de WhatsApp, envío de `window.location.origin` y preservación de firma en descargas.

---

## 3. VERIFICACIÓN

1. **Recargar el Navegador**:
   Haga `Ctrl + Shift + R` (o `Cmd + Shift + R` en Mac) en la pantalla de la Factura de Venta.
2. **Probar Envío por WhatsApp**:
   - Haga clic en **"Compartir Factura"**.
   - Presione **"Abrir en WhatsApp"**.
   - Verifique que el enlace generado en el mensaje sea un hipervínculo completo continuo sin espacios.
3. **Probar Apertura como Cliente (Modo Incógnito / Celular)**:
   - Abra el enlace desde una ventana de incógnito o en el móvil sin sesión iniciada.
   - La factura en PDF se abrirá/descargará directamente sin pedir usuario ni contraseña.
