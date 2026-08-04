import json

with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
    course = json.load(f)

# Flatten articles
articles = []
for step in course["steps"]:
    for article in step["articles"]:
        articles.append(article)

# Generate 6 prompts
batch_size = 10
batches = [articles[i:i + batch_size] for i in range(0, len(articles), batch_size)]

for b_idx, batch in enumerate(batches):
    with open(f"trans_prompt_{b_idx}.txt", "w", encoding="utf-8") as f:
        f.write("Please translate the following Swedish articles into English. Return ONLY a JSON object where the keys are the `article_id` and the values are the English translations.\n\n")
        f.write("```json\n{\n")
        for i, a in enumerate(batch):
            f.write(f'  "{a["article_id"]}": "<your translation>"{"," if i < len(batch)-1 else ""}\n')
        f.write("}\n```\n\nHere are the original Swedish texts:\n\n")
        for a in batch:
            f.write(f"### {a['article_id']}\n{a['sentences'][0]['sv']}\n\n")

print(f"Generated {len(batches)} translation prompts.")
