import json
import os
from generate_chunks_38_54 import all_metas

chunks_dir = "./course/sfid/phase3/data/chunks"

for c in range(38, 55):
    out_path = os.path.join(chunks_dir, f"meta_chunk_{c}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_metas[c], f, ensure_ascii=False, indent=2)
    print(f"Wrote {out_path} ({len(all_metas[c])} entries)")

