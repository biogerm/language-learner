import json

with open("./course/sfid/phase1/master_dictionary.json", "r") as f:
    master = json.load(f)["words"]

with open("./course/sfid/phase3/data/chunks/keys_2.json", "r") as f:
    keys = json.load(f)

# Re-run logic from audit_all.py and print all rejected items
