import json
import re

with open("./course/sfid/phase1/master_dictionary.json", "r") as f:
    master = json.load(f)["words"]

with open("./course/sfid/phase3/data/chunks/keys_2.json", "r") as f:
    keys = json.load(f)

print(f"Total keys in keys_2.json: {len(keys)}")

# Let's inspect words and see translations
