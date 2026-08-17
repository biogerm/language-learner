import fix_audits

print("=== ALL REJECTED WORDS (213) ===")
for idx, (w, reason) in enumerate(fix_audits.rejected):
    tr = fix_audits.master.get(w, {}).get("en", "")
    print(f"{idx+1:3d}. {w:<35} | {reason:<20} | {tr}")

