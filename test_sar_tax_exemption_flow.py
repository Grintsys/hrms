import frappe
from frappe.utils import flt, nowdate

def test_exoneracion_flow():
    frappe.set_user("Administrator")
    print("\n==============================================================")
    print("=== TEST SUITE: FLUJO DE EXONERACION FISCAL SAR HONDURAS ===")
    print("==============================================================")

    company = frappe.get_all("Company")[0]["name"]
    currency = frappe.get_value("Company", company, "default_currency") or "HNL"

    uom = frappe.get_all("UOM")[0]["name"]
    item_group = frappe.get_all("Item Group")[0]["name"]
    customer_group = frappe.get_all("Customer Group")[0]["name"]
    territory = frappe.get_all("Territory")[0]["name"]

    # 1. Asegurar Item de prueba
    item_code = "ITEM-TEST-SAR-115"
    if not frappe.db.exists("Item", item_code):
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": item_code,
            "item_name": "Producto Prueba SAR L115 Incluido",
            "item_group": item_group,
            "stock_uom": uom,
            "is_stock_item": 0
        })
        item.insert(ignore_permissions=True)
        print(f"Item creado: {item_code}")
    else:
        print(f"Item existente: {item_code}")

    # Asegurar Item Price de L 115.00 en Standard Selling
    price_list = frappe.get_all("Price List", filters={"selling": 1}, fields=["name"])
    price_list_name = price_list[0]["name"] if price_list else "Standard Selling"
    if not frappe.db.exists("Price List", price_list_name):
        pl = frappe.get_doc({"doctype": "Price List", "price_list_name": price_list_name, "selling": 1, "currency": currency})
        pl.insert(ignore_permissions=True)

    item_price = frappe.get_all("Item Price", filters={"item_code": item_code, "price_list": price_list_name}, fields=["name"])
    if not item_price:
        ip = frappe.get_doc({
            "doctype": "Item Price",
            "item_code": item_code,
            "price_list": price_list_name,
            "price_list_rate": 115.0,
            "currency": currency
        })
        ip.insert(ignore_permissions=True)
    else:
        frappe.db.set_value("Item Price", item_price[0]["name"], "price_list_rate", 115.0)

    # 2. Crear / Asegurar Clientes de Prueba
    # Cliente 1: Contribuyente
    c1_name = "Cliente Contribuyente Test SAR"
    if not frappe.db.exists("Customer", c1_name):
        c1 = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": c1_name,
            "customer_type": "Company",
            "customer_group": customer_group,
            "territory": territory,
            "tax_category": "Contribuyente"
        })
        c1.insert(ignore_permissions=True)
    else:
        frappe.db.set_value("Customer", c1_name, "tax_category", "Contribuyente")

    # Cliente 2: Diplomático / Misión Internacional
    c2_name = "Embajada Diplomatica Test SAR"
    if not frappe.db.exists("Customer", c2_name):
        c2 = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": c2_name,
            "customer_type": "Company",
            "customer_group": customer_group,
            "territory": territory,
            "tax_category": "Exonerado",
            "custom_subtipo_exonerado": "Diplomático / Misión Internacional",
            "custom_carnet_diplomatico": "CD-HN-998877"
        })
        c2.insert(ignore_permissions=True)
    else:
        frappe.db.set_value("Customer", c2_name, {
            "tax_category": "Exonerado",
            "custom_subtipo_exonerado": "Diplomático / Misión Internacional",
            "custom_carnet_diplomatico": "CD-HN-998877"
        })

    # Cliente 3: Empresa Agrícola con Constancia SAR/SAG
    c3_name = "Agroexportadora Exonerada SAR"
    if not frappe.db.exists("Customer", c3_name):
        c3 = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": c3_name,
            "customer_type": "Company",
            "customer_group": customer_group,
            "territory": territory,
            "tax_category": "Exonerado",
            "custom_subtipo_exonerado": "Constancia SAR / SAG / SEFIN",
            "custom_constancia_exonerado": "REG-EXO-SAR-2026-0099"
        })
        c3.insert(ignore_permissions=True)
    else:
        frappe.db.set_value("Customer", c3_name, {
            "tax_category": "Exonerado",
            "custom_subtipo_exonerado": "Constancia SAR / SAG / SEFIN",
            "custom_constancia_exonerado": "REG-EXO-SAR-2026-0099"
        })

    frappe.db.commit()

    # 3. Test de Facturas
    scenarios = [
        {
            "name": "ESCENARIO 1: CLIENTE CONTRIBUYENTE (ISV 15% INCLUIDO)",
            "customer": c1_name,
            "orden_compra": None,
            "expected_net": 100.0,
            "expected_tax": 15.0,
            "expected_grand_total": 115.0
        },
        {
            "name": "ESCENARIO 2: CLIENTE DIPLOMATICO (EXONERADO 0%)",
            "customer": c2_name,
            "orden_compra": None,
            "expected_net": 100.0,
            "expected_tax": 0.0,
            "expected_grand_total": 100.0
        },
        {
            "name": "ESCENARIO 3: CLIENTE CONSTANCIA SAR/SAG (EXONERADO 0% CON ORDEN DE COMPRA)",
            "customer": c3_name,
            "orden_compra": "OC-EXENTA-SAG-2026-443",
            "expected_net": 100.0,
            "expected_tax": 0.0,
            "expected_grand_total": 100.0
        }
    ]

    all_passed = True

    for sc in scenarios:
        print(f"\n--- Probando {sc['name']} ---")
        si = frappe.new_doc("Sales Invoice")
        si.company = company
        si.customer = sc["customer"]
        si.posting_date = nowdate()
        si.currency = currency
        
        # Simular party details
        from erpnext.accounts.party import get_party_details
        party_details = get_party_details(sc["customer"], party_type="Customer", company=company, posting_date=nowdate())
        si.tax_category = party_details.get("tax_category")
        si.taxes_and_charges = party_details.get("taxes_and_charges")
        
        # Mapear campos personalizados de exoneracion
        cust_doc = frappe.get_doc("Customer", sc["customer"])
        si.custom_subtipo_exonerado = cust_doc.custom_subtipo_exonerado
        si.custom_constancia_exonerado = cust_doc.custom_constancia_exonerado
        si.custom_carnet_diplomatico = cust_doc.custom_carnet_diplomatico
        if sc["orden_compra"]:
            si.custom_orden_compra_exenta = sc["orden_compra"]

        # Agregar Item con precio de lista 115.00
        si.append("items", {
            "item_code": item_code,
            "qty": 1,
            "rate": 115.0,
            "price_list_rate": 115.0
        })

        # Aplicar impuestos y lógica de cálculo
        si.set_taxes()
        si.run_method("before_validate")
        si.calculate_taxes_and_totals()

        net_amount = flt(si.net_total, 2)
        tax_amount = flt(si.total_taxes_and_charges, 2)
        grand_total = flt(si.grand_total, 2)

        print(f"Tax Category asignada: {si.tax_category}")
        print(f"Taxes & Charges Template: {si.taxes_and_charges}")
        print(f"Item Rate en Factura: L {si.items[0].rate:,.2f}")
        print(f"Net Amount (Base Imponible): L {net_amount:,.2f}")
        print(f"ISV Total: L {tax_amount:,.2f}")
        print(f"Grand Total (Total a Pagar): L {grand_total:,.2f}")
        print(f"Variables para Print Format:")
        print(f"  - No. Orden Compra Exenta: {si.custom_orden_compra_exenta or 'N/A'}")
        print(f"  - No. Constancia SAR/SAG:  {si.custom_constancia_exonerado or 'N/A'}")
        print(f"  - No. Carnet Diplomático:  {si.custom_carnet_diplomatico or 'N/A'}")

        # Validaciones
        c_net = abs(net_amount - sc["expected_net"]) < 0.01
        c_tax = abs(tax_amount - sc["expected_tax"]) < 0.01
        c_total = abs(grand_total - sc["expected_grand_total"]) < 0.01

        if c_net and c_tax and c_total:
            print("=> RESULTADO: [VERIFIED / PASS]")
        else:
            print(f"=> RESULTADO: [FAIL] Esperado Net: {sc['expected_net']}, Tax: {sc['expected_tax']}, Total: {sc['expected_grand_total']}")
            all_passed = False

    print("\n==============================================================")
    if all_passed:
        print("=== TODAS LAS PRUEBAS FISCALES SAR FUERON EXITOSAS ===")
    else:
        print("=== ALGUNAS PRUEBAS FALLARON - REVISAR CALCULO ===")
    print("==============================================================\n")

if __name__ == "__main__":
    frappe.init(site="development", sites_path="/workspace/development/frappe-bench/sites")
    frappe.connect()
    try:
        test_exoneracion_flow()
    finally:
        frappe.destroy()
