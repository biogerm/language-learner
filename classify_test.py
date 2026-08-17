import json

with open("./course/sfid/phase1/master_dictionary.json", "r") as f:
    master = json.load(f)["words"]

with open("./course/sfid/phase3/data/chunks/keys_2.json", "r") as f:
    keys = json.load(f)

# Let's inspect each item and check against dictionary / linguistic knowledge
# We will output all items with index, item, translation, and classification.

print(f"Total keys: {len(keys)}")
