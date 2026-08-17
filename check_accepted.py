import fix_audits

# Let's inspect all accepted words and look for potential adverbs, prepositions, phrases, etc.
# We can check word length, spaces, ending, etc.

accepted = fix_audits.accepted

# Let's group accepted words:
multi_word = [w for w in accepted if " " in w]
single_word = [w for w in accepted if " " not in w]

print(f"Total accepted: {len(accepted)}")
print(f"Single word accepted: {len(single_word)}")
print(f"Multi-word accepted: {len(multi_word)}")

print("\n--- ALL MULTI-WORD ACCEPTED ---")
for idx, w in enumerate(multi_word):
    tr = fix_audits.master.get(w, {}).get("en", "")
    print(f"{idx+1:3d}. {w:<35} | {tr}")

