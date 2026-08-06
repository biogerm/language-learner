slash_words = [
    "annat/annan",
    "en gång i månaden/veckan",
    "ska/skall",
    "känna sig/mig",
    "Du med /Du också.",
    "Här är allting toppen/underbart/härligt",
    "Hoppas ni alla/du mår bra!",
    "Du skulle kunna prova/försöka.",
    "alkis /alkoholist",
    "Har du provat/försökt att…?",
    "flintis /flintskallig",
    "tänk dig/er",
    "gå tillbaka till det normala/vanliga",
    "Hur många år har du/han/hon jobbat här?",
    "Har du/ni hört att?",
    "Jag måste berätta en sak/en grej…"
]

unused_words = [
    "Hur många?", "Hur många…?", "Skulle det inte vara bättre att?",
    "Vilken tur att du påminde mig", "annat/annan", "det vill säga",
    "en och en halv", "frihet", "handla med", "högsta dröm", "jaha",
    "lika många", "lämplig", "med mera", "och så vidare", "plocka",
    "respektive", "sedan urminnes tider", "sitta", "skriva",
    "så kallad", "till och med", "tioårsåldern", "toppa", "än att …"
]

# We need to manually define the splits to be grammatically correct based on the context of each phrase.
splits = {
    "annat/annan": ["annat", "annan"],
    "en gång i månaden/veckan": ["en gång i månaden", "en gång i veckan"],
    "ska/skall": ["ska", "skall"],
    "känna sig/mig": ["känna sig", "känna mig"],
    "Du med /Du också.": ["Du med.", "Du också."],
    "Här är allting toppen/underbart/härligt": ["Här är allting toppen", "Här är allting underbart", "Här är allting härligt"],
    "Hoppas ni alla/du mår bra!": ["Hoppas ni alla mår bra!", "Hoppas du mår bra!"],
    "Du skulle kunna prova/försöka.": ["Du skulle kunna prova.", "Du skulle kunna försöka."],
    "alkis /alkoholist": ["alkis", "alkoholist"],
    "Har du provat/försökt att…?": ["Har du provat att…?", "Har du försökt att…?"],
    "flintis /flintskallig": ["flintis", "flintskallig"],
    "tänk dig/er": ["tänk dig", "tänk er"],
    "gå tillbaka till det normala/vanliga": ["gå tillbaka till det normala", "gå tillbaka till det vanliga"],
    "Hur många år har du/han/hon jobbat här?": ["Hur många år har du jobbat här?", "Hur många år har han jobbat här?", "Hur många år har hon jobbat här?"],
    "Har du/ni hört att?": ["Har du hört att?", "Har ni hört att?"],
    "Jag måste berätta en sak/en grej…": ["Jag måste berätta en sak…", "Jag måste berätta en grej…"]
}

final_set = set()

# Process slash words
for w, variants in splits.items():
    for v in variants:
        final_set.add(v)

# Add unused words (if a word is in both, like annat/annan, it was already handled by the split above)
for w in unused_words:
    if w in splits:
        continue # handled by the split
    else:
        final_set.add(w)

print(f"Total split words from the 16 slash terms: {sum(len(v) for v in splits.values())}")
print(f"Total unused words remaining (excluding 'annat/annan'): {len(unused_words) - 1}")
print(f"Total combined unique phrases: {len(final_set)}")

print("\n--- Final List of Phrases ---")
for w in sorted(final_set):
    print(w)

