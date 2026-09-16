import json

base_path = "/Users/vicentegonzalez/Documents/Leaf/V14/frappe_docker14/development/frappe-bench/apps/erpnext/erpnext/accounts/doctype"
bt_path = f"{base_path}/bank_transaction/bank_transaction.json"

with open(bt_path, "r") as f:
    bt_data = json.load(f)

fields = bt_data["fields"]
field_order = bt_data.get("field_order", [])

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

for f in fields:
    if f.get("fieldname") == "party_type":
        f["fieldtype"] = "Select"
        f["options"] = "Customer\nSupplier\nEmployee\nShareholder\nTercero"
    elif f.get("fieldname") == "party":
        f["fieldtype"] = "Dynamic Link"
        f["options"] = "party_type"

if not any(f.get("fieldname") == "custom_beneficiary_name" for f in fields):
    insert_after("party", {
        "fieldname": "custom_beneficiary_name",
        "fieldtype": "Data",
        "label": "Beneficiario Externo",
        "depends_on": "eval:doc.party_type == 'Tercero'"
    })

with open(bt_path, "w") as f:
    json.dump(bt_data, f, indent="\t", separators=(",", ": "))

print("Applied 'Campos Espejo' changes to bank_transaction.json")
