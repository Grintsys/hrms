# PLAN TÉCNICO: COMPARTIR SALES INVOICE COMO PDF MEDIANTE EL SISTEMA NATIVO DEL DISPOSITIVO (ETAPA 1)

## 1. RESUMEN DEL OBJETIVO

Validar la adopción por parte de los usuarios de LEAF ERP al compartir facturas (`Sales Invoice`) en formato PDF directamente a aplicaciones del sistema operativo (WhatsApp, Email, Drive, etc.) utilizando el mecanismo nativo de compartir (`Web Share API` / `navigator.share`).

**Principios clave:**
* **Zero-Fork**: Implementado 100% en la Custom App `leaf` (`apps/leaf`), sin tocar `apps/frappe` ni `apps/erpnext`.
* **Sin integraciones directas con WhatsApp API**: Cero dependencias de Twilio, Meta Business API, webhooks o proveedores externos en esta etapa.
* **Fidelidad al Print Format**: El PDF generado respeta el formato de impresión (`Print Format`) seleccionado por el usuario.
* **Compatibilidad Histórica**: Aplica a facturas nuevas y facturas históricas (hace días, semanas o meses) respetando los permisos nativos de Frappe.
* **Inmutabilidad**: Operación estrictamente de presentación. Cero efectos secundarios en contabilidad, inventario o estado del documento (`docstatus`).

---

## 2. ARQUITECTURA Y FLUJO DE DATOS

```text
  [ Formulario Sales Invoice ]
                │
                ▼
        Botón "Compartir"
                │
                ▼
  [ Diálogo / Selección de Print Format ] (Si aplica)
                │
                ▼
  [ Fetch GET /api/method/frappe.utils.print_format.download_pdf ]
                │
                ▼
     [ Blob PDF -> File Object ] (Nombre: INV-XXXXX.pdf)
                │
         ┌──────┴──────┐
         │             │
  (Soporta Share) (No soporta Share)
         │             │
         ▼             ▼
 [ navigator.share ] [ Fallback: Descarga PDF + Notificación ]
         │
         ▼
  [ Share Sheet Nativo OS ]
   (WhatsApp, AirDrop, Drive, Mail...)
```

---

## 3. INVESTIGACIÓN TÉCNICA Y MATRIZ DE COMPATIBILIDAD

### A. Endpoint Nativo de Frappe para PDF
Frappe v14 expone el método whitelisted:
`/api/method/frappe.utils.print_format.download_pdf`
- **Parámetros**: `doctype`, `name`, `format`, `no_letterhead`, `letterhead`.
- **Seguridad**: Llama internamente a `validate_print_permission(doc)`, asegurando que solo usuarios con permiso de lectura puedan obtener el PDF.

### B. Matriz de Compatibilidad `navigator.share` (Archivos PDF)

| Plataforma | Navegador | Web Share API | Compartir Archivos (`files`) | Resultado / Acción |
| :--- | :--- | :--- | :--- | :--- |
| **Android** | Chrome / Edge | Compatible | Compatible | **Nativo (Share Sheet)** |
| **Android** | Samsung Internet | Compatible | Compatible | **Nativo (Share Sheet)** |
| **iOS / iPadOS** | Safari | Compatible | Compatible | **Nativo (Share Sheet)** |
| **iOS** | Chrome (iOS) | Compatible | Compatible | **Nativo (Share Sheet)** |
| **macOS** | Safari / Chrome | Compatible | Compatible | **Nativo (Share Sheet)** |
| **Windows / Linux**| Chrome / Firefox | Parcial / No | No | **Fallback (Descarga + Aviso)** |
| **Entorno HTTP (sin SSL)**| Todos | Deshabilitado | Deshabilitado | **Fallback (Descarga + Aviso)** |

---

## 4. ESTRATEGIA DE FALLBACK

Cuando `navigator.canShare` retorne `false` o la API no esté disponible en el navegador/dispositivo:
1. El sistema descargará automáticamente el archivo PDF generado (`INV-XXXX.pdf`).
2. Se desplegará un mensaje informativo en español neutro:
   > *"El dispositivo o navegador no soporta compartir archivos directamente. El PDF de la factura ha sido descargado en su dispositivo para que pueda compartirlo manualmente."*

---

## 5. ANALÍTICA DE ADOPCIÓN (MEDICIÓN DE USO)

Para cumplir con el objetivo de validar la adopción por parte de los usuarios, se incluirá un registro liviano no invasivo:
- **DocType**: `Leaf Share Log` (o método whitelisted backend `leaf.controllers.share_analytics.log_share_event`).
- **Campos registrados**: `user`, `doctype`, `docname`, `print_format`, `timestamp`, `share_method` (`native` / `fallback`).
- **Privacidad**: No se registra destinatario, número telefónico ni contenido del documento.

---

## 6. PLAN DE IMPLEMENTACIÓN (COMPONENTES)

1. **Custom App `leaf`**:
   - Registrar `doctype_js = {"Sales Invoice": "public/js/sales_invoice.js"}` en `apps/leaf/leaf/hooks.py`.
   - Crear `apps/leaf/leaf/public/js/sales_invoice.js` para añadir el botón "Compartir" en el formulario de `Sales Invoice`.
   - Implementar el generador de PDF client-side usando `fetch` blob y `navigator.share`.
   - Implementar el modal/selector de `Print Format` cuando existan múltiples formatos definidos.
2. **Backend Analytics**:
   - Crear endpoint whitelisted `leaf.controllers.share_analytics.log_share_event` en `apps/leaf/leaf/controllers/share_analytics.py`.
3. **DocType de Registros / Analytics**:
   - Crear `Leaf Share Log` mediante script de configuración / DocType declarativo en `leaf`.

---

## 7. MATRIZ DE PRUEBAS DE ACEPTACIÓN

1. **Factura Nueva**: Crear `Sales Invoice`, hacer Submit -> Pulsar "Compartir" -> Verificar generación de PDF y Share Sheet.
2. **Factura Histórica**: Abrir una `Sales Invoice` antigua -> Pulsar "Compartir" -> Verificar generación correcta.
3. **Variación de Print Format**: Cambiar Print Format seleccionado -> Verificar que el PDF generado corresponde al formato elegido.
4. **Prueba en Dispositivo Móvil (Android/iOS)**: Seleccionar WhatsApp desde el menú nativo de compartir -> Verificar envío correcto del archivo PDF.
5. **Prueba de Fallback**: Simular ambiente sin `navigator.share` -> Verificar descarga de PDF y mensaje descriptivo.
6. **Prueba de Inmutabilidad**: Verificar que el estado del documento, fecha, totales e inventario no sufran ninguna modificación tras la acción.
7. **Prueba de Permisos**: Verificar que un usuario sin permiso de lectura no pueda descargar ni compartir la factura.
