import os
import json
import frappe

def setup_sar_exemption_report():
    frappe.set_user("Administrator")
    print("=== CREANDO REPORTE FISCAL: REPORTE DE VENTAS EXONERADAS SAR ===")

    # 1. Actualizar datos históricos en Sales Invoice
    frappe.db.sql("""
        UPDATE `tabSales Invoice`
        SET exonerated_amount = net_total,
            exempt_amount = 0.0
        WHERE tax_category IN ('Exonerado', 'EXONERADO')
          AND (exonerated_amount = 0.0 OR exonerated_amount IS NULL)
    """)
    frappe.db.commit()
    print("Datos históricos de Sales Invoice actualizados.")

    # 2. Directorio del reporte en erpnext
    report_dir = "/workspace/development/frappe-bench/apps/erpnext/erpnext/accounts/report/reporte_de_ventas_exoneradas_sar"
    os.makedirs(report_dir, exist_ok=True)

    # 3. JSON del reporte
    report_json = {
        "add_total_row": 1,
        "columns": [],
        "creation": "2026-10-08 19:45:00",
        "disabled": 0,
        "docstatus": 0,
        "doctype": "Report",
        "is_standard": "Yes",
        "letter_head": "",
        "modified": "2026-10-08 19:45:00",
        "modified_by": "Administrator",
        "module": "Accounts",
        "name": "Reporte de Ventas Exoneradas SAR",
        "owner": "Administrator",
        "prepared_report": 0,
        "ref_doctype": "Sales Invoice",
        "report_name": "Reporte de Ventas Exoneradas SAR",
        "report_type": "Script Report",
        "roles": [
            {"role": "Accounts Manager"},
            {"role": "Accounts User"},
            {"role": "Sales Manager"},
            {"role": "Sales User"}
        ]
    }
    with open(os.path.join(report_dir, "reporte_de_ventas_exoneradas_sar.json"), "w", encoding="utf-8") as f:
        json.dump(report_json, f, indent=1)

    # 4. JS del reporte
    report_js = """// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Reporte de Ventas Exoneradas SAR"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Empresa"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        },
        {
            "fieldname": "from_date",
            "label": __("Desde Fecha"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_start(),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("Hasta Fecha"),
            "fieldtype": "Date",
            "default": frappe.datetime.now_date(),
            "reqd": 1
        },
        {
            "fieldname": "customer",
            "label": __("Cliente"),
            "fieldtype": "Link",
            "options": "Customer"
        },
        {
            "fieldname": "custom_subtipo_exonerado",
            "label": __("Subtipo de Exoneración"),
            "fieldtype": "Select",
            "options": "\\nConstancia SAR / SAG / SEFIN\\nDiplomático / Misión Internacional\\nDecreto / Ley Especial"
        }
    ]
};
"""
    with open(os.path.join(report_dir, "reporte_de_ventas_exoneradas_sar.js"), "w", encoding="utf-8") as f:
        f.write(report_js)

    # 5. Python del reporte
    report_py = """# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate

def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "posting_date", "fieldtype": "Date", "label": _("Fecha"), "width": 100},
        {"fieldname": "name", "fieldtype": "Link", "options": "Sales Invoice", "label": _("No. Factura"), "width": 160},
        {"fieldname": "customer_name", "fieldtype": "Data", "label": _("Nombre del Cliente"), "width": 180},
        {"fieldname": "tax_id", "fieldtype": "Data", "label": _("RTN / Identificación"), "width": 130},
        {"fieldname": "subtipo", "fieldtype": "Data", "label": _("Régimen / Subtipo"), "width": 160},
        {"fieldname": "constancia_sar", "fieldtype": "Data", "label": _("No. Constancia SAR/SAG"), "width": 160},
        {"fieldname": "orden_compra", "fieldtype": "Data", "label": _("No. Orden Compra Exenta"), "width": 160},
        {"fieldname": "carnet_diplo", "fieldtype": "Data", "label": _("No. Carnet Diplomático"), "width": 150},
        {"fieldname": "exonerated_amount", "fieldtype": "Currency", "label": _("Base Exonerada"), "width": 130},
        {"fieldname": "isv_exonerado_estimado", "fieldtype": "Currency", "label": _("ISV Ahorrado (15%)"), "width": 130},
        {"fieldname": "grand_total", "fieldtype": "Currency", "label": _("Total Facturado"), "width": 130},
        {"fieldname": "cai", "fieldtype": "Data", "label": _("CAI Fiscal"), "width": 180},
        {"fieldname": "pos_profile", "fieldtype": "Link", "options": "POS Profile", "label": _("Caja / POS"), "width": 120}
    ]

def get_data(filters):
    company = filters.get("company")
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    if not (company and from_date and to_date):
        return []

    where = [
        "si.docstatus = 1",
        "si.company = %(company)s",
        "si.posting_date BETWEEN %(from_date)s AND %(to_date)s",
        "(si.tax_category IN ('Exonerado', 'EXONERADO') OR si.exonerated_amount > 0)"
    ]
    params = {"company": company, "from_date": from_date, "to_date": to_date}

    if filters.get("customer"):
        where.append("si.customer = %(customer)s")
        params["customer"] = filters.get("customer")

    if filters.get("custom_subtipo_exonerado"):
        where.append("si.custom_subtipo_exonerado = %(subtipo)s")
        params["subtipo"] = filters.get("custom_subtipo_exonerado")

    rows = frappe.db.sql(
        f'''
        SELECT
            si.posting_date,
            si.name,
            si.customer,
            si.customer_name,
            si.custom_subtipo_exonerado AS subtipo,
            si.custom_constancia_exonerado AS constancia_sar,
            si.custom_orden_compra_exenta AS orden_compra,
            si.custom_carnet_diplomatico AS carnet_diplo,
            si.exonerated_amount,
            si.net_total,
            si.grand_total,
            COALESCE(si.cai, '') AS cai,
            si.pos_profile
        FROM `tabSales Invoice` si
        WHERE {" AND ".join(where)}
        ORDER BY si.posting_date, si.name
        ''',
        params,
        as_dict=True
    )

    if not rows:
        return []

    # Obtener RTN
    customer_names = list({r["customer"] for r in rows if r.get("customer")})
    tax_ids = {}
    if customer_names:
        tax_ids = {
            c["name"]: c["tax_id"]
            for c in frappe.get_all("Customer", filters={"name": ["in", customer_names]}, fields=["name", "tax_id"])
        }

    data = []
    for r in rows:
        base_exo = flt(r.get("exonerated_amount") or r.get("net_total"))
        isv_ahorro = flt(base_exo * 0.15, 2)
        
        row = {
            "posting_date": r.get("posting_date"),
            "name": r.get("name"),
            "customer_name": r.get("customer_name") or r.get("customer"),
            "tax_id": tax_ids.get(r.get("customer")) or "",
            "subtipo": r.get("subtipo") or "Exoneración General",
            "constancia_sar": r.get("constancia_sar") or "",
            "orden_compra": r.get("orden_compra") or "",
            "carnet_diplo": r.get("carnet_diplo") or "",
            "exonerated_amount": base_exo,
            "isv_exonerado_estimado": isv_ahorro,
            "grand_total": flt(r.get("grand_total")),
            "cai": r.get("cai"),
            "pos_profile": r.get("pos_profile") or ""
        }
        data.append(row)

    return data
"""
    with open(os.path.join(report_dir, "reporte_de_ventas_exoneradas_sar.py"), "w", encoding="utf-8") as f:
        f.write(report_py)

    # 6. Registrar en Base de Datos DocType Report
    rep_name = "Reporte de Ventas Exoneradas SAR"
    if not frappe.db.exists("Report", rep_name):
        doc = frappe.get_doc({
            "doctype": "Report",
            "report_name": rep_name,
            "report_type": "Script Report",
            "ref_doctype": "Sales Invoice",
            "module": "Accounts",
            "is_standard": "Yes"
        })
        doc.insert(ignore_permissions=True)
        print(f"Reporte registrado en Frappe: {rep_name}")
    else:
        doc = frappe.get_doc("Report", rep_name)
        doc.is_standard = "Yes"
        doc.module = "Accounts"
        doc.save(ignore_permissions=True)
        print(f"Reporte actualizado en Frappe: {rep_name}")

    frappe.db.commit()
    print("=== CONFIGURACION DE REPORTES FISCALES COMPLETADA EXITOSAMENTE ===")

if __name__ == "__main__":
    frappe.init(site="development", sites_path="/workspace/development/frappe-bench/sites")
    frappe.connect()
    try:
        setup_sar_exemption_report()
    finally:
        frappe.destroy()
