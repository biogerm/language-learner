import json

def is_suspicious(word):
    # Common english words/suffixes that aren't Swedish
    w = word.lower()
    if w in ["book", "climate", "eyes,", "ntally", "freedom", "open", "minded", "dream", "have"]:
        return True
    if w.endswith("ly") and not w.endswith("kalkyl") and w != "förtjänt av(att)bli": # mostly english adverbs
        return True
    if w.endswith("tion") and not (w.endswith("ation") or w.endswith("ektion") or w.endswith("ktion")):
        # Swedish words end in -tion too, but let's be careful
        pass
    if " freedom" in w or "open-minded" in w or "have a dream" in w:
        return True
    return False

def main():
    with open("all_bases.txt", "r", encoding="utf-8") as f:
        bases = [line.strip() for line in f]
        
    for b in bases:
        if is_suspicious(b):
            print(f"Suspicious: {b}")

if __name__ == "__main__":
    main()
