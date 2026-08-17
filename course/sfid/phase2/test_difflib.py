import difflib
import re

sv = "Jag gissar att mindre än hälften av oss vanligt folk faktiskt förstår all den komplicerade teknik vi använder."
base = "faktisk"
words = re.findall(r'[a-zA-ZåäöÅÄÖ]+', sv)

matches = difflib.get_close_matches(base, words, n=1, cutoff=0.6)
print(f"base: {base}, match: {matches}")

sv2 = "Det var en spännande statistik som visade tydligt att spenderar vi i genomsnitt ungefär tre timmar varje kväll framför en teveskärm i vardagsrummet."
base2 = "teve"
words2 = re.findall(r'[a-zA-ZåäöÅÄÖ]+', sv2)
matches2 = difflib.get_close_matches(base2, words2, n=1, cutoff=0.6)
print(f"base: {base2}, match: {matches2}")

