import json, os, glob

unused = [
    "Hur många?", "Hur många…?", "Skulle det inte vara bättre att?",
    "Vilken tur att du påminde mig", "annat/annan", "det vill säga",
    "en och en halv", "frihet", "handla med", "högsta dröm", "jaha",
    "lika många", "lämplig", "med mera", "och så vidare", "plocka",
    "respektive", "sedan urminnes tider", "sitta", "skriva",
    "så kallad", "till och med", "tioårsåldern", "toppa", "än att …"
]

sources = glob.glob("../data/*.json")
word_to_source = {w: [] for w in unused}

for src in sources:
    with open(src, 'r') as f:
        try:
            data = json.load(f)
            src_name = os.path.basename(src)
            # data is usually a dict of word -> translation or list of objects
            if isinstance(data, dict):
                for w in unused:
                    if w in data:
                        word_to_source[w].append(src_name)
            elif isinstance(data, list):
                # if list of objects with "sv" or something
                for item in data:
                    if isinstance(item, dict):
                        for w in unused:
                            # Try to match key or any value
                            if w in item.values() or w in item:
                                word_to_source[w].append(src_name)
        except Exception:
            pass

print("=== Unused Words Sources ===")
for w, srcs in word_to_source.items():
    if not srcs:
        print(f"- {w}: [Could not locate in source JSONs, might be from PDF extraction]")
    else:
        print(f"- {w}: {', '.join(set(srcs))}")

