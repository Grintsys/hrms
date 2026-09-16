import json
import os

base_path = "/Users/vicentegonzalez/Documents/Leaf/V14/frappe_docker14/development/frappe-bench/apps/erpnext/erpnext/accounts/doctype"
bt_path = f"{base_path}/bank_transaction/bank_transaction.json"

with open(bt_path, "r") as f:
    bt_data = json.load(f)

fields = bt_data["fields"]
field_order = bt_data.get("field_order", [])

# Remove entity_type, beneficiary_type, beneficiary
fields_to_remove = ["entity_type", "beneficiary_type", "beneficiary"]
bt_data["fields"] = [f for f in fields if f.get("fieldname") not in fields_to_remove]
bt_data["field_order"] = [f for f in field_order if f not in fields_to_remove]
fields = bt_data["fields"]

def insert_after(fieldname, new_field):
    idx = -1
    for i, f in enumerate(fields):
        if f.get("fieldname") == fieldname:
            idx = i
            break
    if idx != -1:
        fields.insert(idx + 1, new_field)
    else:
        fields.append(new_field)
    if new_field["fieldname"] not in bt_data["field_order"]:
        try:
            o_idx = bt_data["field_order"].index(fieldname)
            bt_data["field_order"].insert(o_idx + 1, new_field["fieldname"])
        except ValueError:
            bt_data["field_order"].append(new_field["fieldname"])

# Mod party_type 
for f in fields:
    if f.get("fieldname") == "party_type":
        f["fieldtype"] = "Select"
        f["options"] = "Customer\nSupplier\nEmployee\nTercero"
    elif f.get("fieldname") == "transaction_type":
        f["fieldtype"] = "Select"
        f["options"] = "Cheque\nTransferencia\nDébito\nDepósito\nCrédito"
    elif f.get("fieldname") == "deposit":
        f["depends_on"] = "eval:in_list(['Depósito', 'Crédito', 'Crédito Bancario'], doc.transaction_type)"
    elif f.get("fieldname") == "withdrawal":
        f["depends_on"] = "eval:in_list(['Cheque', 'Transferencia', 'Débito'], doc.transaction_type)"

# Add check_number if not exists
if not any(f.get("fieldname") == "check_number" for f in fields):
    insert_after("transaction_type", {
        "fieldname": "check_number",
        "fieldtype": "Data",
        "label": "Número de Cheque",
        "depends_on": "eval:doc.transaction_type == 'Cheque'"
    })

with open(bt_path, "w") as f:
    json.dump(bt_data, f, indent="\t", separators=(",", ": "))

print("JSON updated")

