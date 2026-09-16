# DOCUMENTACIÓN DE IMPLEMENTACIÓN Y CORRECCIÓN: COMPARTIR SALES INVOICE COMO PDF (ETAPA 1)

## 1. RESUMEN DE LA SOLUCIÓN

Se ha corregido y optimizado la **Etapa 1: Compartir Sales Invoice como PDF mediante el Sistema Nativo del Dispositivo** en LEAF ERP v14.

### Diagnóstico de la Causa Raíz del Bloqueo ("Failed to fetch"):
En entornos de desarrollo o con servidor monohilo (Werkzeug / `bench start`), la función nativa `frappe.utils.print_format.download_pdf` hacía que `wkhtmltopdf` intentara realizar peticiones HTTP de regreso a `http://127.0.0.1:8000` o `http://development:8000` para descargar imágenes y CSS. Al estar el único hilo del servidor ocupado procesando la llamada original de PDF, se producía un **interbloqueo de red (deadlock)**, lo que congelaba el servidor y retornaba `Failed to fetch` tras 30+ segundos.

### Solución Implementada (100% Zero-Fork):
Se implementó un generador de PDF seguro y ultra-rápido en la Custom App `leaf` (`apps/leaf/leaf/controllers/share_analytics.py`):
1. Captura la plantilla HTML del Print Format seleccionado.
2. Convierte todas las URLs relativas y HTTP de activos/archivos a rutas locales de sistema de archivos (`file://...`).
3. Ejecuta `wkhtmltopdf` en modo de lectura local directa sin realizar ninguna petición de red HTTP.
4. Renderiza el PDF en **menos de 1 segundo** (ejemplo probado: 24,595 bytes sin bloqueos).

---

## 2. ARCHIVOS MODIFICADOS Y CREADOS

### A. Backend (`apps/leaf/leaf/controllers/share_analytics.py`)
- Método whitelisted `leaf.controllers.share_analytics.download_pdf`:
  - Valida permisos de lectura del usuario sobre la factura (`doc.check_permission("read")`).
  - Convierte URLs de assets a `file://`.
  - Configura `enable-local-file-access` e ignora advertencias de red externas.
  - Retorna la respuesta binaria PDF con cabecera `Content-Type: application/pdf`.

### B. Frontend (`apps/leaf/leaf/public/js/sales_invoice.js`)
- Actualizada la llamada `fetch` para invocar `/api/method/leaf.controllers.share_analytics.download_pdf`.
- Integra el selector de `Print Format`, la invocación de `navigator.share` y la estrategia de fallback automática.

---

## 3. INSTRUCCIONES PARA VERIFICAR EN EL NAVEGADOR

1. **Reiniciar o Descongelar Servidor Dev** (Si habías bloqueado el proceso `bench start` manualmente, vuelve a iniciarlo).
2. **Refrescar el Navegador**:
   Haga `Ctrl + Shift + R` (o `Cmd + Shift + R` en Mac) en la pantalla de LEAF ERP para limpiar la caché de JS.
3. **Probar la Acción**:
   - Abra cualquier factura de venta (`Sales Invoice`), ej. `000-001-01-00000601`.
   - Haga clic en **"Compartir PDF"**.
   - El PDF se generará de manera **inmediata** (sin congelar el sistema) y abrirá el Share Sheet nativo del dispositivo (WhatsApp, Mail, Drive, etc.) o descargará el PDF en fallback si no dispone de Share Sheet.
