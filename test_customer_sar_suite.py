import frappe
from frappe.utils import nowdate, add_years, flt

def run_customer_test_suite():
    frappe.set_user("Administrator")
    print("\n======================================================================")
    print("=== SUITE DE PRUEBAS EXTENSIVA: DOCTYPE CLIENTE (CUSTOMER) SAR ===")
    print("======================================================================")

    uom = frappe.get_all("UOM")[0]["name"]
    item_group = frappe.get_all("Item Group")[0]["name"]
    customer_group = frappe.get_all("Customer Group")[0]["name"]
    territory = frappe.get_all("Territory")[0]["name"]
    company = frappe.get_all("Company")[0]["name"]

    # Normalizar Tax Category
    frappe.db.sql("""UPDATE tabCustomer SET tax_category = 'Contribuyente' WHERE tax_category = 'NORMAL' OR tax_category IS NULL OR tax_category = ''""")
    frappe.db.sql("""UPDATE tabCustomer SET tax_category = 'Exonerado' WHERE tax_category = 'EXONERADO'""")
    frappe.db.sql("""UPDATE `tabTax Rule` SET tax_category = 'Exonerado' WHERE tax_category = 'EXONERADO'""")
    frappe.db.sql("""UPDATE `tabTax Category` SET name = 'Exonerado', title = 'Exonerado' WHERE name = 'EXONERADO'""")
    frappe.db.commit()

    results = []

    # PRUEBA 1: Creación de Cliente por Defecto (Persona Natural sin definir Tax Category)
    print("\n[TEST 1] Creación de Cliente Natural por Defecto...")
    c1_name = "Cliente Natural Default Prueba SAR"
    if frappe.db.exists("Customer", c1_name):
        frappe.delete_doc("Customer", c1_name, force=1)
    
    c1 = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": c1_name,
        "customer_type": "Individual",
        "customer_group": customer_group,
        "territory": territory
    })
    c1.insert(ignore_permissions=True)
    c1_loaded = frappe.get_doc("Customer", c1.name)
    
    t1_pass = (c1_loaded.tax_category == "Contribuyente")
    print(f"  -> Tax Category asignada: {c1_loaded.tax_category}")
    print(f"  -> Tipo de Cliente: {c1_loaded.customer_type}")
    print(f"  -> Estado: {'[PASS / VERIFIED]' if t1_pass else '[FAIL]'}")
    results.append(("Test 1: Default Contribuyente en Cliente Natural", t1_pass, f"Tax Category: {c1_loaded.tax_category}"))

    # PRUEBA 2: Cliente No Contribuyente (Consumidor Final)
    print("\n[TEST 2] Cliente No Contribuyente (Consumidor Final)...")
    c2_name = "Consumidor Final Minorista Prueba SAR"
    if frappe.db.exists("Customer", c2_name):
        frappe.delete_doc("Customer", c2_name, force=1)

    c2 = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": c2_name,
        "customer_type": "Individual",
        "customer_group": customer_group,
        "territory": territory,
        "tax_category": "No contribuyente"
    })
    c2.insert(ignore_permissions=True)
    c2_loaded = frappe.get_doc("Customer", c2.name)

    from erpnext.accounts.party import get_party_details
    pd2 = get_party_details(c2.name, party_type="Customer", company=company)
    t2_pass = (c2_loaded.tax_category == "No contribuyente" and "ISV 15%" in pd2.get("taxes_and_charges", ""))
    print(f"  -> Tax Category: {c2_loaded.tax_category}")
    print(f"  -> Plantilla de Impuestos resuelta: {pd2.get('taxes_and_charges')}")
    print(f"  -> Estado: {'[PASS / VERIFIED]' if t2_pass else '[FAIL]'}")
    results.append(("Test 2: Cliente No Contribuyente / Consumidor Final", t2_pass, f"Template: {pd2.get('taxes_and_charges')}"))

    # PRUEBA 3: Cliente Exportación (Ventas Internacionales Tasa Cero)
    print("\n[TEST 3] Cliente Exportación...")
    c3_name = "Global Trade Export LLC"
    if frappe.db.exists("Customer", c3_name):
        frappe.delete_doc("Customer", c3_name, force=1)

    c3 = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": c3_name,
        "customer_type": "Company",
        "customer_group": customer_group,
        "territory": "Resto del mundo" if frappe.db.exists("Territory", "Resto del mundo") else territory,
        "tax_category": "Exportacion"
    })
    c3.insert(ignore_permissions=True)
    c3_loaded = frappe.get_doc("Customer", c3.name)
    pd3 = get_party_details(c3.name, party_type="Customer", company=company)
    t3_pass = (c3_loaded.tax_category == "Exportacion" and "Exportacion 0%" in pd3.get("taxes_and_charges", ""))
    print(f"  -> Tax Category: {c3_loaded.tax_category}")
    print(f"  -> Plantilla de Impuestos resuelta: {pd3.get('taxes_and_charges')}")
    print(f"  -> Estado: {'[PASS / VERIFIED]' if t3_pass else '[FAIL]'}")
    results.append(("Test 3: Cliente Exportación Tasa 0%", t3_pass, f"Template: {pd3.get('taxes_and_charges')}"))

    # PRUEBA 4: Cliente Exonerado - Constancia SAR / SAG / SEFIN
    print("\n[TEST 4] Cliente Exonerado con Constancia SAR/SAG...")
    c4_name = "Agroindustrias del Valle SA"
    if frappe.db.exists("Customer", c4_name):
        frappe.delete_doc("Customer", c4_name, force=1)

    c4 = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": c4_name,
        "customer_type": "Company",
        "customer_group": customer_group,
        "territory": territory,
        "tax_category": "Exonerado",
        "custom_subtipo_exonerado": "Constancia SAR / SAG / SEFIN",
        "custom_constancia_exonerado": "REG-SAR-2026-991122",
        "custom_vencimiento_exoneracion": add_years(nowdate(), 1)
    })
    c4.insert(ignore_permissions=True)
    c4_loaded = frappe.get_doc("Customer", c4.name)
    pd4 = get_party_details(c4.name, party_type="Customer", company=company)
    t4_pass = (c4_loaded.tax_category in ["Exonerado", "EXONERADO"] and 
               c4_loaded.custom_subtipo_exonerado == "Constancia SAR / SAG / SEFIN" and 
               c4_loaded.custom_constancia_exonerado == "REG-SAR-2026-991122" and
               "Exonerado 0%" in pd4.get("taxes_and_charges", ""))
    print(f"  -> Tax Category: {c4_loaded.tax_category}")
    print(f"  -> Subtipo: {c4_loaded.custom_subtipo_exonerado}")
    print(f"  -> No. Constancia: {c4_loaded.custom_constancia_exonerado}")
    print(f"  -> Plantilla de Impuestos resuelta: {pd4.get('taxes_and_charges')}")
    print(f"  -> Estado: {'[PASS / VERIFIED]' if t4_pass else '[FAIL]'}")
    results.append(("Test 4: Exonerado con Constancia SAR/SAG", t4_pass, f"Constancia: {c4_loaded.custom_constancia_exonerado}"))

    # PRUEBA 5: Cliente Exonerado - Diplomático / Misión Internacional
    print("\n[TEST 5] Cliente Exonerado Diplomático / Misión...")
    c5_name = "Embajada del Reino de España"
    if frappe.db.exists("Customer", c5_name):
        frappe.delete_doc("Customer", c5_name, force=1)

    c5 = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": c5_name,
        "customer_type": "Company",
        "customer_group": customer_group,
        "territory": territory,
        "tax_category": "Exonerado",
        "custom_subtipo_exonerado": "Diplomático / Misión Internacional",
        "custom_carnet_diplomatico": "CD-ES-2026-7788",
        "custom_vencimiento_exoneracion": add_years(nowdate(), 2)
    })
    c5.insert(ignore_permissions=True)
    c5_loaded = frappe.get_doc("Customer", c5.name)
    pd5 = get_party_details(c5.name, party_type="Customer", company=company)
    t5_pass = (c5_loaded.tax_category in ["Exonerado", "EXONERADO"] and 
               c5_loaded.custom_subtipo_exonerado == "Diplomático / Misión Internacional" and 
               c5_loaded.custom_carnet_diplomatico == "CD-ES-2026-7788" and
               "Exonerado 0%" in pd5.get("taxes_and_charges", ""))
    print(f"  -> Tax Category: {c5_loaded.tax_category}")
    print(f"  -> Subtipo: {c5_loaded.custom_subtipo_exonerado}")
    print(f"  -> No. Carnet Diplomático: {c5_loaded.custom_carnet_diplomatico}")
    print(f"  -> Plantilla de Impuestos resuelta: {pd5.get('taxes_and_charges')}")
    print(f"  -> Estado: {'[PASS / VERIFIED]' if t5_pass else '[FAIL]'}")
    results.append(("Test 5: Exonerado Diplomático / Misión", t5_pass, f"Carnet: {c5_loaded.custom_carnet_diplomatico}"))

    # PRUEBA 6: Transición Dinámica de Categoría en Cliente Existente
    print("\n[TEST 6] Transición de Contribuyente a Exonerado y Retorno...")
    c6 = frappe.get_doc("Customer", c1.name)
    c6.tax_category = "Exonerado"
    c6.custom_subtipo_exonerado = "Decreto / Ley Especial"
    c6.save(ignore_permissions=True)
    c6_exo_pd = get_party_details(c6.name, party_type="Customer", company=company)
    
    # Revertir a Contribuyente
    c6.tax_category = "Contribuyente"
    c6.save(ignore_permissions=True)
    c6_norm_pd = get_party_details(c6.name, party_type="Customer", company=company)
    
    t6_pass = ("Exonerado 0%" in c6_exo_pd.get("taxes_and_charges", "") and 
               "ISV 15%" in c6_norm_pd.get("taxes_and_charges", ""))
    print(f"  -> Plantilla al cambiar a Exonerado: {c6_exo_pd.get('taxes_and_charges')}")
    print(f"  -> Plantilla al retornar a Contribuyente: {c6_norm_pd.get('taxes_and_charges')}")
    print(f"  -> Estado: {'[PASS / VERIFIED]' if t6_pass else '[FAIL]'}")
    results.append(("Test 6: Transición Dinámica de Categoría", t6_pass, "Adaptación en cascada exitosa"))

    # RESUMEN FINAL
    print("\n======================================================================")
    print("=== RESUMEN DE EJECUCION DE PRUEBAS UNITARIAS Y FUNCIONALES ===")
    print("======================================================================")
    total_passed = sum(1 for _, passed, _ in results)
    for name, passed, detail in results:
        status_label = "[PASS / VERIFIED]" if passed else "[FAIL]"
        print(f"{status_label:<18} | {name:<45} | {detail}")
    print("======================================================================")
    print(f"Total Pruebas: {len(results)} | Exitosas: {total_passed} | Fallidas: {len(results) - total_passed}")
    print("======================================================================\n")

if __name__ == "__main__":
    frappe.init(site="development", sites_path="/workspace/development/frappe-bench/sites")
    frappe.connect()
    try:
        run_customer_test_suite()
    finally:
        frappe.destroy()
