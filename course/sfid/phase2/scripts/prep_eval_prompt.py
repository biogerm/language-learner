import json

with open("discrepancies.json", "r", encoding="utf-8") as f:
    discrepancies = json.load(f)

prompt = """You are an expert Swedish linguist. We have extracted Swedish vocabulary words from texts, and mapped them to their English contextual meaning ("contextual_en").
However, we also have a master dictionary meaning ("master_en").
Below is a list of discrepancies where "contextual_en" differs from "master_en".
Your task is to identify ONLY the cases where "contextual_en" is a HALLUCINATION or COMPLETELY WRONG mapping (e.g., mapping a pronoun to an unrelated adjective, or a totally wrong word due to AI confusion).
If "contextual_en" is just a valid synonym, alternative phrasing, or correct contextual adaptation of "master_en" (e.g., "lazy days" vs "days of leisure"), you MUST NOT flag it.

Output ONLY a JSON list of strings, where each string is formatted as "sentence_id:::base_form" for the ones that are TRULY WRONG.
Do not output anything else.

Discrepancies to evaluate:
"""

for sid, data in discrepancies.items():
    prompt += f"\n--- {sid} ---\n"
    prompt += f"sv: {data['sv_sentence']}\n"
    prompt += f"en: {data['en_sentence']}\n"
    for w in data["words"]:
        prompt += f"  Word: {w['base_form']} | contextual_en: {w['contextual_en']} | master_en: {w['master_en']}\n"

with open("prompts/eval_prompt.txt", "w", encoding="utf-8") as f:
    f.write(prompt)

print("Prompt prepared.")
