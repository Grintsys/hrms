# DOCUMENTACIÓN DE IMPLEMENTACIÓN: COMPARTIR SALES INVOICE (WHATSAPP + PDF)

## 1. RESUMEN DE LA SOLUCIÓN

Se ha implementado una solución robusta y multiplataforma para **Compartir Facturas de Venta (Sales Invoice)** directamente hacia **WhatsApp / WhatsApp Business** y descarga/impresión de **PDF** en LEAF ERP v14.

### Limitación previa de `navigator.share({ files })`:
Los navegadores móviles de terceros en iOS (Chrome, Edge, Firefox) y navegadores de escritorio (Chrome en macOS/Windows) restringen la API de compartir archivos binarios (`files: [pdf]`), causando fallbacks no deseados o mensajes de bloqueo.

### Solución Implementada:
Un modal inteligente de alta disponibilidad que ofrece:
1. **Envío Directo a WhatsApp / WhatsApp Business (`wa.me`)**:
   - Autocompleta automáticamente el número celular del cliente (`Customer.mobile_no` o `Contact`).
   - Soporta números locales de Honduras (8 dígitos -> agrega automáticamente prefijo `504`) e internacionales.
   - Mensaje prediseñado en español neutro con el nombre del cliente, número de factura, monto total formateado y enlace directo al PDF.
   - Permite al usuario editar o personalizar el mensaje antes de enviar.
2. **Descarga Directa de PDF**:
   - Genera y descarga el archivo PDF sin bloqueos ni retrasos.
3. **Ver / Imprimir**:
   - Abre la vista de impresión en una pestaña nueva con el formato seleccionado.
4. **Compartir Nativo (Sistema)**:
   - Si el dispositivo soporta `navigator.share`, permite compartir el texto y enlace hacia cualquier otra app instalada (AirDrop, Correo, Telegram, etc.).

---

## 2. ARCHIVOS MODIFICADOS Y CREADOS

### A. Backend (`erpnext/accounts/doctype/sales_invoice/share_invoice.py`)
- `get_share_details(doctype, name, format=None)`:
  - Obtiene datos de contacto del cliente, teléfono celular, totales formateados y URL del PDF.
- `download_pdf(doctype, name, format=None, no_letterhead=0, letterhead=None)`:
  - Generador de PDF ultra-rápido y seguro contra bloqueos de red locales.
- `log_share_event(doctype, name, print_format=None, share_method=None)`:
  - Registro anónimo de eventos de uso y adopción (`whatsapp`, `download`, `native_share`).

### B. Frontend (`erpnext/accounts/doctype/sales_invoice/sales_invoice.js`)
- Botón **"Compartir Factura"** en la barra superior y en el menú de "Acciones".
- Modal interactivo con selector de formato de impresión, teléfono, mensaje editable y botón destacado de WhatsApp en verde oficial (`#25D366`).

---

## 3. CÓMO PROBAR EN EL NAVEGADOR

1. **Recargar el Navegador**:
   Haga `Ctrl + Shift + R` (o `Cmd + Shift + R` en Mac) en la pantalla de la Factura de Venta para refrescar el código JavaScript.
2. **Abrir una Factura de Venta**:
   - Presione el botón **"Compartir Factura"**.
   - Se abrirá el modal con el teléfono del cliente autocompletado y el mensaje con el enlace al PDF listo.
   - Al pulsar **"Abrir en WhatsApp"**, se abrirá directamente el chat de WhatsApp con el mensaje cargado.
   - Si prefiere el archivo en su dispositivo, use **"Descargar PDF"** o **"Ver / Imprimir"**.
