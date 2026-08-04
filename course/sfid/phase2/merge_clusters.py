import json
import os

def main():
    merged = {
        "Vardagsliv": [],
        "Arbetsliv": [],
        "Hälsa & Medicin": [],
        "Natur & Miljö": [],
        "Samhälle & Politik": [],
        "Kultur & Nöje": [],
        "Relationer & Känslor": [],
        "Vetenskap & Teknik": [],
        "Resor & Transport": [],
        "Mat & Matlagning": [],
        "Utbildning": [],
        "Abstrakta Koncept": []
    }
    
    for i in range(1, 4):
        file_path = f"cluster_out_{i}.json"
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for k, v in data.items():
                for expected_k in merged.keys():
                    if expected_k in k or expected_k.split()[0] in k:
                        merged[expected_k].extend(v)
                        break

    # verify total count
    total = sum(len(v) for v in merged.values())
    print(f"Merged {total} words into clustered_dictionary.json")
    
    with open("clustered_dictionary.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
