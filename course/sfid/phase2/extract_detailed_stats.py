import json

with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
    course = json.load(f)

markdown_output = "\n## Detailed Article Breakdown\n\n"

total_articles = 0
for step in course["steps"]:
    theme_title = step["step_title"]
    articles = step["articles"]
    num_articles = len(articles)
    total_articles += num_articles
    
    total_theme_words = sum(a["target_word_count"] for a in articles)
    
    markdown_output += f"### {theme_title}\n"
    markdown_output += f"- **Total Articles**: {num_articles}\n"
    markdown_output += f"- **Total Target Words**: {total_theme_words}\n\n"
    
    markdown_output += "| Article ID | Article Title | Target Words Used (B1) |\n"
    markdown_output += "|---|---|---|\n"
    
    for a in articles:
        article_id = a["article_id"]
        title = a["article_title"]
        word_count = a["target_word_count"]
        markdown_output += f"| {article_id} | {title} | {word_count} |\n"
        
    markdown_output += "\n"

# Append to phase2_statistics.md
with open("phase2_statistics.md", "a", encoding="utf-8") as f:
    f.write(markdown_output)

print("Detailed statistics appended to phase2_statistics.md")
