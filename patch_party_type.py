import json

base_path = "/Users/vicentegonzalez/Documents/Leaf/V14/frappe_docker14/development/frappe-bench/apps/erpnext/erpnext/accounts/doctype"
bt_path = f"{base_path}/bank_transaction/bank_transaction.json"

with open(bt_path, "r") as f:
    bt_data = json.load(f)

for f in bt_data["fields"]:
    if f.get("fieldname") == "party":
        # Make the generic type Data to avoid backend dynamic link validation crashes for 'Tercero'
        f["fieldtype"] = "Data"
        # We can leave options as "party_type" or remove it, does not matter if fieldtype is Data on backend
        break

with open(bt_path, "w") as f:
    json.dump(bt_data, f, indent="\t", separators=(",", ": "))

print("Party converted to Data to bypass strict link validation.")
