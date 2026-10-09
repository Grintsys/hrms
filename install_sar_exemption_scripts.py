import frappe

def install_scripts():
    frappe.set_user("Administrator")
    print("=== INSTALANDO CLIENT SCRIPTS Y SERVER SCRIPTS PARA SAR EXONERACION ===")

    # 1. Client Script en Sales Invoice
    cs_script_content = """
frappe.ui.form.on('Sales Invoice', {
    customer: function(frm) {
        if (!frm.doc.customer) return;
        frappe.db.get_value('Customer', frm.doc.customer, 
            ['tax_category', 'custom_subtipo_exonerado', 'custom_constancia_exonerado', 'custom_carnet_diplomatico'], 
            function(r) {
                if (r) {
                    if (r.tax_category) frm.set_value('tax_category', r.tax_category);
                    frm.set_value('custom_subtipo_exonerado', r.custom_subtipo_exonerado || '');
                    frm.set_value('custom_constancia_exonerado', r.custom_constancia_exonerado || '');
                    frm.set_value('custom_carnet_diplomatico', r.custom_carnet_diplomatico || '');
                    frm.trigger('adjust_exonerated_rates');
                }
            }
        );
    },
    
    tax_category: function(frm) {
        frm.trigger('adjust_exonerated_rates');
    },

    adjust_exonerated_rates: function(frm) {
        if (frm.doc.tax_category === 'Exonerado' || frm.doc.tax_category === 'EXONERADO') {
            $.each(frm.doc.items || [], function(i, item) {
                if (item.price_list_rate && (!item.discount_percentage || item.discount_percentage === 0)) {
                    // Si el precio de lista incluye el 15% de ISV, calcular base neta sin impuesto
                    var net_rate = flt(item.price_list_rate / 1.15, precision('rate', item));
                    if (Math.abs(item.rate - item.price_list_rate) < 0.01) {
                        frappe.model.set_value(item.doctype, item.name, 'rate', net_rate);
                    }
                }
            });
            frm.refresh_field('items');
        }
    },

    validate: function(frm) {
        if (frm.doc.tax_category === 'Exonerado' || frm.doc.tax_category === 'EXONERADO') {
            if (frm.doc.custom_subtipo_exonerado === 'Constancia SAR / SAG / SEFIN') {
                if (!frm.doc.custom_orden_compra_exenta) {
                    frappe.msgprint({
                        title: __('Validación SAR Honduras'),
                        message: __('Para clientes con Constancia SAR/SAG, es obligatorio ingresar el No. de Orden de Compra Exenta.'),
                        indicator: 'orange'
                    });
                }
            } else if (frm.doc.custom_subtipo_exonerado === 'Diplomático / Misión Internacional') {
                if (!frm.doc.custom_carnet_diplomatico) {
                    frappe.msgprint({
                        title: __('Validación SAR Honduras'),
                        message: __('Para Diplomáticos / Misiones, es obligatorio ingresar el No. de Carnet Diplomático.'),
                        indicator: 'orange'
                    });
                }
            }
        }
    }
});

frappe.ui.form.on('Sales Invoice Item', {
    item_code: function(frm, cdt, cdn) {
        setTimeout(function() {
            frm.trigger('adjust_exonerated_rates');
        }, 800);
    }
});
"""

    cs_name = "SAR Exoneracion - Sales Invoice Handler"
    if frappe.db.exists("Client Script", cs_name):
        frappe.db.set_value("Client Script", cs_name, "script", cs_script_content)
        frappe.db.set_value("Client Script", cs_name, "enabled", 1)
        print(f"Client Script actualizado: {cs_name}")
    else:
        cs = frappe.get_doc({
            "doctype": "Client Script",
            "name": cs_name,
            "dt": "Sales Invoice",
            "view": "Form",
            "enabled": 1,
            "script": cs_script_content
        })
        cs.insert(ignore_permissions=True)
        print(f"Client Script creado: {cs_name}")

    # 2. Server Script en Sales Invoice
    ss_script_content = """
if doc.tax_category in ['Exonerado', 'EXONERADO']:
    # Ajustar rates de items si provienen de lista con impuesto incluido
    for item in doc.items:
        if item.price_list_rate and not item.discount_percentage:
            # Si el rate era igual al precio de lista con 15% incluido, extraer la base sin ISV
            if abs(float(item.rate or 0) - float(item.price_list_rate or 0)) < 0.01:
                item.rate = round(float(item.price_list_rate) / 1.15, 2)
                item.amount = round(float(item.rate) * float(item.qty or 1), 2)

    # Validaciones obligatorias para Submit
    if doc.docstatus == 1:
        if doc.custom_subtipo_exonerado == 'Constancia SAR / SAG / SEFIN':
            if not doc.custom_orden_compra_exenta:
                frappe.throw("SAR Honduras: Para emitir una factura exonerada con Constancia SAR/SAG, es obligatorio registrar el No. de Orden de Compra Exenta.")
            if not doc.custom_constancia_exonerado:
                frappe.throw("SAR Honduras: Debe especificar el No. de Constancia de Registro de Exonerados.")
        elif doc.custom_subtipo_exonerado == 'Diplomático / Misión Internacional':
            if not doc.custom_carnet_diplomatico:
                frappe.throw("SAR Honduras: Debe registrar el No. de Carnet Diplomático o de Misión Internacional.")
"""

    ss_name = "SAR Exoneracion - Sales Invoice Server Logic"
    if frappe.db.exists("Server Script", ss_name):
        frappe.db.set_value("Server Script", ss_name, "script", ss_script_content)
        frappe.db.set_value("Server Script", ss_name, "disabled", 0)
        print(f"Server Script actualizado: {ss_name}")
    else:
        ss = frappe.get_doc({
            "doctype": "Server Script",
            "name": ss_name,
            "script_type": "DocType Event",
            "reference_doctype": "Sales Invoice",
            "doctype_event": "Before Validate",
            "disabled": 0,
            "script": ss_script_content
        })
        ss.insert(ignore_permissions=True)
        print(f"Server Script creado: {ss_name}")

    frappe.db.commit()
    print("=== CLIENT Y SERVER SCRIPTS INSTALADOS CON EXITO ===")

if __name__ == "__main__":
    frappe.init(site="development", sites_path="/workspace/development/frappe-bench/sites")
    frappe.connect()
    try:
        install_scripts()
    finally:
        frappe.destroy()
