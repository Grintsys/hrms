import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def run():
    frappe.set_user("Administrator")
    print("=== INICIANDO CONFIGURACION SAR HONDURAS (EXONERACION) ===")
    
    # 1. Crear Tax Categories
    tax_categories = ["Contribuyente", "No contribuyente", "Exportacion", "Exonerado"]
    for tc in tax_categories:
        if not frappe.db.exists("Tax Category", tc):
            doc = frappe.get_doc({"doctype": "Tax Category", "title": tc})
            doc.insert(ignore_permissions=True)
            print(f"Tax Category creada: {tc}")
        else:
            print(f"Tax Category ya existe: {tc}")

    # 2. Obtener compañía principal
    companies = frappe.get_all("Company", fields=["name", "default_currency", "abbr"])
    if not companies:
        print("No se encontraron compañías.")
        return
    company = companies[0]["name"]
    abbr = companies[0]["abbr"]
    print(f"Compañía de trabajo: {company} ({abbr})")

    # 3. Buscar o crear cuentas de impuestos (cuentas de tipo detalle / is_group = 0)
    # Buscar grupo de impuestos
    tax_groups = frappe.get_all("Account", filters={"company": company, "account_type": "Tax", "is_group": 1}, fields=["name"])
    if not tax_groups:
        tax_groups = frappe.get_all("Account", filters={"company": company, "account_name": ["like", "%IMPUESTOS%"], "is_group": 1}, fields=["name"])
    
    parent_tax_group = tax_groups[0]["name"] if tax_groups else None
    if not parent_tax_group:
        liabilities = frappe.get_all("Account", filters={"company": company, "root_type": "Liability", "is_group": 1}, fields=["name"])
        parent_tax_group = liabilities[0]["name"] if liabilities else None

    # Cuenta de detalle para ISV 15%
    tax_account_name = f"Débito Fiscal ISV 15% - {abbr}"
    if not frappe.db.exists("Account", tax_account_name):
        acc = frappe.get_doc({
            "doctype": "Account",
            "account_name": "Débito Fiscal ISV 15%",
            "company": company,
            "parent_account": parent_tax_group,
            "account_type": "Tax",
            "root_type": "Liability",
            "is_group": 0
        })
        acc.insert(ignore_permissions=True)
        print(f"Cuenta de detalle creada: {tax_account_name}")
    else:
        print(f"Cuenta de detalle existente: {tax_account_name}")

    # Cuenta de detalle para Exonerado 0%
    exo_account_name = f"Débito Fiscal ISV Exonerado 0% - {abbr}"
    if not frappe.db.exists("Account", exo_account_name):
        acc = frappe.get_doc({
            "doctype": "Account",
            "account_name": "Débito Fiscal ISV Exonerado 0%",
            "company": company,
            "parent_account": parent_tax_group,
            "account_type": "Tax",
            "root_type": "Liability",
            "is_group": 0
        })
        acc.insert(ignore_permissions=True)
        print(f"Cuenta creada: {exo_account_name}")
    else:
        # Asegurar is_group = 0 si ya fue creada
        frappe.db.set_value("Account", exo_account_name, "is_group", 0)
        print(f"Cuenta existente: {exo_account_name}")

    # 4. Crear Sales Taxes and Charges Templates
    # Plantilla A: HN - ISV 15% (Impuesto Incluido)
    tpl_contrib_title = "HN - ISV 15% (Impuesto Incluido)"
    existing_contrib = frappe.get_all("Sales Taxes and Charges Template", filters={"company": company, "title": tpl_contrib_title}, fields=["name"])
    if not existing_contrib:
        doc = frappe.get_doc({
            "doctype": "Sales Taxes and Charges Template",
            "title": tpl_contrib_title,
            "company": company,
            "is_default": 1,
            "taxes": [
                {
                    "charge_type": "On Net Total",
                    "account_head": tax_account_name,
                    "description": "ISV 15% (Incluido)",
                    "rate": 15.0,
                    "included_in_print_rate": 1
                }
            ]
        })
        doc.insert(ignore_permissions=True)
        tpl_contrib_name = doc.name
        print(f"Plantilla creada: {tpl_contrib_name}")
    else:
        tpl_contrib_name = existing_contrib[0]["name"]
        print(f"Plantilla ya existe: {tpl_contrib_name}")

    # Plantilla B: HN - Exonerado 0%
    tpl_exo_title = "HN - Exonerado 0%"
    existing_exo = frappe.get_all("Sales Taxes and Charges Template", filters={"company": company, "title": tpl_exo_title}, fields=["name"])
    if not existing_exo:
        doc = frappe.get_doc({
            "doctype": "Sales Taxes and Charges Template",
            "title": tpl_exo_title,
            "company": company,
            "taxes": [
                {
                    "charge_type": "On Net Total",
                    "account_head": exo_account_name,
                    "description": "ISV Exonerado 0%",
                    "rate": 0.0,
                    "included_in_print_rate": 1
                }
            ]
        })
        doc.insert(ignore_permissions=True)
        tpl_exo_name = doc.name
        print(f"Plantilla creada: {tpl_exo_name}")
    else:
        tpl_exo_name = existing_exo[0]["name"]
        print(f"Plantilla ya existe: {tpl_exo_name}")

    # Plantilla C: HN - Exportacion 0%
    tpl_exp_title = "HN - Exportacion 0%"
    existing_exp = frappe.get_all("Sales Taxes and Charges Template", filters={"company": company, "title": tpl_exp_title}, fields=["name"])
    if not existing_exp:
        doc = frappe.get_doc({
            "doctype": "Sales Taxes and Charges Template",
            "title": tpl_exp_title,
            "company": company,
            "taxes": [
                {
                    "charge_type": "On Net Total",
                    "account_head": exo_account_name,
                    "description": "Exportación Tasa 0%",
                    "rate": 0.0,
                    "included_in_print_rate": 0
                }
            ]
        })
        doc.insert(ignore_permissions=True)
        tpl_exp_name = doc.name
        print(f"Plantilla creada: {tpl_exp_name}")
    else:
        tpl_exp_name = existing_exp[0]["name"]
        print(f"Plantilla ya existe: {tpl_exp_name}")

    # 5. Configurar Tax Rules automáticas
    tax_rules_config = [
        {"tax_category": "Contribuyente", "template": tpl_contrib_name},
        {"tax_category": "No contribuyente", "template": tpl_contrib_name},
        {"tax_category": "Exonerado", "template": tpl_exo_name},
        {"tax_category": "Exportacion", "template": tpl_exp_name},
    ]

    for tr_cfg in tax_rules_config:
        existing = frappe.get_all("Tax Rule", filters={"company": company, "tax_category": tr_cfg["tax_category"], "tax_type": "Sales"}, fields=["name"])
        if not existing:
            tr = frappe.get_doc({
                "doctype": "Tax Rule",
                "tax_type": "Sales",
                "tax_category": tr_cfg["tax_category"],
                "sales_tax_template": tr_cfg["template"],
                "company": company,
                "priority": 1
            })
            tr.insert(ignore_permissions=True)
            print(f"Tax Rule creada para: {tr_cfg['tax_category']} -> {tr_cfg['template']}")
        else:
            print(f"Tax Rule ya existe para: {tr_cfg['tax_category']}")

    # 6. Custom Fields en Customer y Sales Invoice
    custom_fields = {
        "Customer": [
            {
                "fieldname": "custom_sar_section",
                "label": "Información Fiscal SAR (Honduras)",
                "fieldtype": "Section Break",
                "insert_after": "tax_category"
            },
            {
                "fieldname": "custom_subtipo_exonerado",
                "label": "Subtipo de Exoneración",
                "fieldtype": "Select",
                "options": "Constancia SAR / SAG / SEFIN\nDiplomático / Misión Internacional\nDecreto / Ley Especial",
                "depends_on": "eval:doc.tax_category=='Exonerado'",
                "insert_after": "custom_sar_section"
            },
            {
                "fieldname": "custom_constancia_exonerado",
                "label": "No. Constancia Reg. Exonerados (SAR/SAG)",
                "fieldtype": "Data",
                "depends_on": "eval:doc.tax_category=='Exonerado' && doc.custom_subtipo_exonerado=='Constancia SAR / SAG / SEFIN'",
                "insert_after": "custom_subtipo_exonerado"
            },
            {
                "fieldname": "custom_carnet_diplomatico",
                "label": "No. Carnet Diplomático / Misión",
                "fieldtype": "Data",
                "depends_on": "eval:doc.tax_category=='Exonerado' && doc.custom_subtipo_exonerado=='Diplomático / Misión Internacional'",
                "insert_after": "custom_constancia_exonerado"
            },
            {
                "fieldname": "custom_vencimiento_exoneracion",
                "label": "Fecha Vencimiento Exoneración",
                "fieldtype": "Date",
                "depends_on": "eval:doc.tax_category=='Exonerado'",
                "insert_after": "custom_carnet_diplomatico"
            }
        ],
        "Sales Invoice": [
            {
                "fieldname": "custom_sar_invoice_section",
                "label": "Datos de Exoneración SAR (Honduras)",
                "fieldtype": "Section Break",
                "depends_on": "eval:doc.tax_category=='Exonerado'",
                "insert_after": "tax_category"
            },
            {
                "fieldname": "custom_subtipo_exonerado",
                "label": "Subtipo de Exoneración",
                "fieldtype": "Data",
                "read_only": 1,
                "fetch_from": "customer.custom_subtipo_exonerado",
                "depends_on": "eval:doc.tax_category=='Exonerado'",
                "insert_after": "custom_sar_invoice_section"
            },
            {
                "fieldname": "custom_orden_compra_exenta",
                "label": "No. Orden de Compra Exenta SAR",
                "fieldtype": "Data",
                "depends_on": "eval:doc.tax_category=='Exonerado'",
                "insert_after": "custom_subtipo_exonerado"
            },
            {
                "fieldname": "custom_constancia_exonerado",
                "label": "No. Constancia Reg. Exonerados (SAR/SAG)",
                "fieldtype": "Data",
                "fetch_from": "customer.custom_constancia_exonerado",
                "depends_on": "eval:doc.tax_category=='Exonerado'",
                "insert_after": "custom_orden_compra_exenta"
            },
            {
                "fieldname": "custom_carnet_diplomatico",
                "label": "No. Carnet Diplomático / Misión",
                "fieldtype": "Data",
                "fetch_from": "customer.custom_carnet_diplomatico",
                "depends_on": "eval:doc.tax_category=='Exonerado'",
                "insert_after": "custom_constancia_exonerado"
            }
        ]
    }

    create_custom_fields(custom_fields, update=True)
    print("Custom fields creados/actualizados exitosamente.")

    # 7. Property Setter: Tax Category Default = "Contribuyente"
    make_property_setter(
        doctype="Customer",
        fieldname="tax_category",
        property="default",
        value="Contribuyente",
        property_type="Data"
    )
    print("Property Setter para Customer.tax_category default = 'Contribuyente' aplicado.")

    # 8. Actualizar clientes existentes sin tax_category a 'Contribuyente'
    frappe.db.sql("""
        UPDATE `tabCustomer` 
        SET tax_category = 'Contribuyente' 
        WHERE tax_category IS NULL OR tax_category = ''
    """)
    frappe.db.commit()
    print("Clientes existentes actualizados a 'Contribuyente'.")
    print("=== CONFIGURACION SAR COMPLETADA EXITOSAMENTE ===")

if __name__ == "__main__":
    frappe.init(site="development", sites_path="/workspace/development/frappe-bench/sites")
    frappe.connect()
    try:
        run()
    finally:
        frappe.destroy()
