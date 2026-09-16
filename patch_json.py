import json
import os

def insert_after(fields, fieldname, new_field):
    idx = -1
    for i, f in enumerate(fields):
        if f.get("fieldname") == fieldname:
            idx = i
            break
    if idx != -1:
        fields.insert(idx + 1, new_field)
    else:
        fields.append(new_field)

base_path = "/Users/vicentegonzalez/Documents/Leaf/V14/frappe_docker14/development/frappe-bench/apps/erpnext/erpnext/accounts/doctype"

# 1. Update Bank Account
ba_path = f"{base_path}/bank_account/bank_account.json"
with open(ba_path, "r") as f:
    ba_data = json.load(f)

if not any(f.get("fieldname") == "check_correlative" for f in ba_data["fields"]):
    new_field = {
        "fieldname": "check_correlative",
        "fieldtype": "Int",
        "label": "Correlativo de Cheques",
        "default": "0",
    }
    insert_after(ba_data["fields"], "bank_account_no", new_field)
    
    # Must also update "field_order"
    if "check_correlative" not in ba_data.get("field_order", []):
        idx = ba_data["field_order"].index("bank_account_no") if "bank_account_no" in ba_data["field_order"] else -1
        if idx != -1:
            ba_data["field_order"].insert(idx + 1, "check_correlative")
        else:
            ba_data["field_order"].append("check_correlative")

with open(ba_path, "w") as f:
    json.dump(ba_data, f, indent="\t", separators=(",", ": "))


# 2. Update Bank Transaction
bt_path = f"{base_path}/bank_transaction/bank_transaction.json"
with open(bt_path, "r") as f:
    bt_data = json.load(f)

fields = bt_data["fields"]
field_order = bt_data.get("field_order", [])

def add_field(data, insert_after_field, new_f):
    if not any(f.get("fieldname") == new_f["fieldname"] for f in data["fields"]):
        insert_after(data["fields"], insert_after_field, new_f)
        if new_f["fieldname"] not in data.get("field_order", []):
            try:
                idx = data["field_order"].index(insert_after_field)
                data["field_order"].insert(idx + 1, new_f["fieldname"])
            except ValueError:
                data["field_order"].append(new_f["fieldname"])

# Update transaction_type
for f in fields:
    if f.get("fieldname") == "transaction_type":
        f["fieldtype"] = "Select"
        f["options"] = "Cheque\\nTransferencia\\nDébito\\nDepósito\\nCrédito"
        break

add_field(bt_data, "date", {
    "fieldname": "entity_type",
    "fieldtype": "Select",
    "label": "Tipo de Entidad",
    "options": "Cliente\\nProveedor\\nEmpleado\\nTercero"
})

add_field(bt_data, "entity_type", {
    "fieldname": "beneficiary_type",
    "fieldtype": "Data",
    "hidden": 1,
    "label": "Beneficiary Type"
})

add_field(bt_data, "beneficiary_type", {
    "fieldname": "beneficiary",
    "fieldtype": "Dynamic Link",
    "label": "Beneficiario",
    "options": "beneficiary_type"
})

add_field(bt_data, "custom_journal_entries", {
    "fieldname": "totals_section",
    "fieldtype": "Section Break",
    "label": "Totales"
})

add_field(bt_data, "totals_section", {
    "fieldname": "total_debit",
    "fieldtype": "Currency",
    "label": "Total Debe",
    "options": "currency",
    "read_only": 1
})

add_field(bt_data, "total_debit", {
    "fieldname": "total_credit",
    "fieldtype": "Currency",
    "label": "Total Haber",
    "options": "currency",
    "read_only": 1
})

add_field(bt_data, "total_credit", {
    "fieldname": "difference",
    "fieldtype": "Currency",
    "label": "Diferencia",
    "options": "currency",
    "read_only": 1
})

with open(bt_path, "w") as f:
    json.dump(bt_data, f, indent="\t", separators=(",", ": "))
    # Frappe appends curly braces on exactly the line or something, json.dump mostly handles it.

print("JSON files patched successfully.")
