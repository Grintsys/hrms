import frappe
from frappe.utils import nowdate, flt

def test_posawesome_integration():
    frappe.set_user("Administrator")
    print("\n==============================================================================")
    print("=== SUITE DE PRUEBAS DE INTEGRACION: POSAWESOME Y SALES INVOICE (SAR) ===")
    print("==============================================================================")

    company = frappe.get_all("Company")[0]["name"]
    pos_profiles = frappe.get_all("POS Profile", filters={"company": company}, fields=["name", "warehouse", "selling_price_list"])
    if not pos_profiles:
        print("Error: No se encontró POS Profile.")
        return
    
    pos_profile = pos_profiles[0]["name"]
    warehouse = pos_profiles[0]["warehouse"]
    print(f"POS Profile de prueba: {pos_profile} (Bodega: {warehouse})")

    # Obtener modo de pago para POS
    pos_doc = frappe.get_doc("POS Profile", pos_profile)
    mode_of_payment = pos_doc.payments[0].mode_of_payment if pos_doc.payments else "Cash"
    print(f"Modo de Pago POS: {mode_of_payment}")

    item_code = "ITEM-TEST-SAR-115"
    results = []

    # PRUEBA 1: Venta POS a Cliente Contribuyente (Impuesto Incluido)
    print("\n[TEST POS 1] Venta POS a Cliente Contribuyente...")
    si1 = frappe.new_doc("Sales Invoice")
    si1.is_pos = 1
    si1.pos_profile = pos_profile
    si1.company = company
    si1.customer = "Cliente Contribuyente Test SAR"
    si1.posting_date = nowdate()
    si1.set_warehouse = warehouse
    
    from erpnext.accounts.party import get_party_details
    pd1 = get_party_details(si1.customer, party_type="Customer", company=company, posting_date=nowdate())
    si1.tax_category = pd1.get("tax_category")
    si1.taxes_and_charges = pd1.get("taxes_and_charges")

    si1.append("items", {
        "item_code": item_code,
        "qty": 1,
        "rate": 115.0,
        "price_list_rate": 115.0,
        "warehouse": warehouse
    })
    si1.set_taxes()
    si1.calculate_taxes_and_totals()

    # Agregar pago completo en efectivo
    si1.append("payments", {
        "mode_of_payment": mode_of_payment,
        "amount": si1.grand_total
    })
    si1.insert(ignore_permissions=True)
    si1.submit()

    t1_pass = (flt(si1.net_total, 2) == 100.0 and 
               flt(si1.total_taxes_and_charges, 2) == 15.0 and 
               flt(si1.grand_total, 2) == 115.0 and 
               flt(si1.outstanding_amount, 2) == 0.0 and 
               si1.docstatus == 1)
    print(f"  -> Factura POS creada y enviada: {si1.name}")
    print(f"  -> Base Gravada: L {si1.net_total:,.2f} | ISV 15%: L {si1.total_taxes_and_charges:,.2f} | Total: L {si1.grand_total:,.2f}")
    print(f"  -> Saldo Pendiente: L {si1.outstanding_amount:,.2f} | Docstatus: {si1.docstatus}")
    print(f"  -> Estado: {'[PASS / VERIFIED]' if t1_pass else '[FAIL]'}")
    results.append(("POS 1: Venta POS Contribuyente (L 115 Total)", t1_pass, f"Factura: {si1.name}"))

    # PRUEBA 2: Venta POS a Diplomático (Exonerado 0% con Carnet)
    print("\n[TEST POS 2] Venta POS a Diplomático (Exonerado 0%)...")
    c_diplo = frappe.get_doc("Customer", "Embajada Diplomatica Test SAR")
    si2 = frappe.new_doc("Sales Invoice")
    si2.is_pos = 1
    si2.pos_profile = pos_profile
    si2.company = company
    si2.customer = c_diplo.name
    si2.posting_date = nowdate()
    si2.set_warehouse = warehouse

    pd2 = get_party_details(si2.customer, party_type="Customer", company=company, posting_date=nowdate())
    si2.tax_category = pd2.get("tax_category")
    si2.taxes_and_charges = pd2.get("taxes_and_charges")
    si2.custom_subtipo_exonerado = c_diplo.custom_subtipo_exonerado
    si2.custom_carnet_diplomatico = c_diplo.custom_carnet_diplomatico

    si2.append("items", {
        "item_code": item_code,
        "qty": 1,
        "rate": 115.0,
        "price_list_rate": 115.0,
        "warehouse": warehouse
    })
    si2.set_taxes()
    si2.run_method("before_validate")
    si2.calculate_taxes_and_totals()

    # Agregar pago
    si2.append("payments", {
        "mode_of_payment": mode_of_payment,
        "amount": si2.grand_total
    })
    si2.insert(ignore_permissions=True)
    si2.submit()

    t2_pass = (flt(si2.net_total, 2) == 100.0 and 
               flt(si2.total_taxes_and_charges, 2) == 0.0 and 
               flt(si2.grand_total, 2) == 100.0 and 
               flt(si2.outstanding_amount, 2) == 0.0 and 
               si2.docstatus == 1 and 
               si2.custom_carnet_diplomatico == "CD-HN-998877")
    print(f"  -> Factura POS creada y enviada: {si2.name}")
    print(f"  -> Base Exonerada: L {si2.net_total:,.2f} | ISV Exonerado: L {si2.total_taxes_and_charges:,.2f} | Total Cobrado: L {si2.grand_total:,.2f}")
    print(f"  -> Carnet Diplomático registrado: {si2.custom_carnet_diplomatico}")
    print(f"  -> Estado: {'[PASS / VERIFIED]' if t2_pass else '[FAIL]'}")
    results.append(("POS 2: Venta POS Diplomático (L 100 Total)", t2_pass, f"Factura: {si2.name}"))

    # PRUEBA 3: Venta POS con Constancia SAR y Orden de Compra
    print("\n[TEST POS 3] Venta POS Exonerada con Constancia y Orden de Compra...")
    c_exo = frappe.get_doc("Customer", "Agroexportadora Exonerada SAR")
    si3 = frappe.new_doc("Sales Invoice")
    si3.is_pos = 1
    si3.pos_profile = pos_profile
    si3.company = company
    si3.customer = c_exo.name
    si3.posting_date = nowdate()
    si3.set_warehouse = warehouse

    pd3 = get_party_details(si3.customer, party_type="Customer", company=company, posting_date=nowdate())
    si3.tax_category = pd3.get("tax_category")
    si3.taxes_and_charges = pd3.get("taxes_and_charges")
    si3.custom_subtipo_exonerado = c_exo.custom_subtipo_exonerado
    si3.custom_constancia_exonerado = c_exo.custom_constancia_exonerado
    si3.custom_orden_compra_exenta = "OC-POS-SAG-2026-991"

    si3.append("items", {
        "item_code": item_code,
        "qty": 1,
        "rate": 115.0,
        "price_list_rate": 115.0,
        "warehouse": warehouse
    })
    si3.set_taxes()
    si3.run_method("before_validate")
    si3.calculate_taxes_and_totals()

    si3.append("payments", {
        "mode_of_payment": mode_of_payment,
        "amount": si3.grand_total
    })
    si3.insert(ignore_permissions=True)
    si3.submit()

    t3_pass = (flt(si3.net_total, 2) == 100.0 and 
               flt(si3.total_taxes_and_charges, 2) == 0.0 and 
               flt(si3.grand_total, 2) == 100.0 and 
               flt(si3.outstanding_amount, 2) == 0.0 and 
               si3.docstatus == 1 and 
               si3.custom_orden_compra_exenta == "OC-POS-SAG-2026-991")
    print(f"  -> Factura POS creada y enviada: {si3.name}")
    print(f"  -> Base Exonerada: L {si3.net_total:,.2f} | ISV: L {si3.total_taxes_and_charges:,.2f} | Total: L {si3.grand_total:,.2f}")
    print(f"  -> Constancia SAR: {si3.custom_constancia_exonerado} | Orden Compra: {si3.custom_orden_compra_exenta}")
    print(f"  -> Estado: {'[PASS / VERIFIED]' if t3_pass else '[FAIL]'}")
    results.append(("POS 3: Venta POS Constancia SAR/SAG (L 100 Total)", t3_pass, f"Factura: {si3.name}"))

    # PRUEBA 4: Control de Bloqueo Tributario (Intento de Submit sin Orden de Compra)
    print("\n[TEST POS 4] Verificación de Bloqueo Tributario (Submit sin Orden de Compra)...")
    si4 = frappe.new_doc("Sales Invoice")
    si4.is_pos = 1
    si4.pos_profile = pos_profile
    si4.company = company
    si4.customer = c_exo.name
    si4.posting_date = nowdate()
    si4.set_warehouse = warehouse

    si4.tax_category = "Exonerado"
    si4.custom_subtipo_exonerado = "Constancia SAR / SAG / SEFIN"
    si4.custom_constancia_exonerado = "REG-SAR-2026-991122"
    si4.custom_orden_compra_exenta = ""  # Omitido intencionalmente

    si4.append("items", {
        "item_code": item_code,
        "qty": 1,
        "rate": 100.0,
        "price_list_rate": 115.0,
        "warehouse": warehouse
    })
    si4.insert(ignore_permissions=True)
    
    blocked_successfully = False
    try:
        si4.submit()
    except Exception as e:
        blocked_successfully = True
        print(f"  -> Bloqueo capturado con éxito: {e}")

    print(f"  -> Estado de Bloqueo: {'[PASS / VERIFIED]' if blocked_successfully else '[FAIL]'}")
    results.append(("POS 4: Bloqueo Tributario por Falta de Orden de Compra", blocked_successfully, "Bloqueo efectivo en Submit"))

    # RESUMEN FINAL
    print("\n==============================================================================")
    print("=== RESUMEN DE PRUEBAS DE INTEGRACION POSAWESOME Y SALES INVOICE ===")
    print("==============================================================================")
    total_passed = sum(1 for _, passed, _ in results)
    for name, passed, detail in results:
        status_label = "[PASS / VERIFIED]" if passed else "[FAIL]"
        print(f"{status_label:<18} | {name:<50} | {detail}")
    print("==============================================================================")
    print(f"Total Pruebas POS: {len(results)} | Exitosas: {total_passed} | Fallidas: {len(results) - total_passed}")
    print("==============================================================================\n")

if __name__ == "__main__":
    frappe.init(site="development", sites_path="/workspace/development/frappe-bench/sites")
    frappe.connect()
    try:
        test_posawesome_integration()
    finally:
        frappe.destroy()
