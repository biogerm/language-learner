import json
import glob

files = sorted(glob.glob("articles_translated/art_*.json"))

total_target_words = 0
total_secondary_words = 0
secondary_word_freq = {}

report = "# Phase 2 目标词与拓展词精细化提取统计报告\n\n"
report += "以下是对所有 57 篇文章提取、校验和最终翻译注入情况的详细统计。\n\n"
report += "## 📈 1. 总体数据总结\n\n"

article_stats = []

for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    art_id = filepath.split('/')[-1].replace('.json', '')
    t_words = 0
    s_words = 0
    
    for s in data["sentences"]:
        t_words += len(s.get("target_words", []))
        s_list = s.get("secondary_words", [])
        s_words += len(s_list)
        
        for sw in s_list:
            bf = sw["base_form"]
            secondary_word_freq[bf] = secondary_word_freq.get(bf, 0) + 1
            
    total_target_words += t_words
    total_secondary_words += s_words
    
    article_stats.append(f"| {art_id} | {t_words} | {s_words} |")

report += f"- **处理文章总数**: {len(files)} 篇\n"
report += f"- **精准注入翻译的 Target Words (目标大纲词) 总人次**: {total_target_words}\n"
report += f"- **自发提取并注入翻译的 Secondary Words (高难度拓展词) 总人次**: {total_secondary_words}\n\n"

report += "## 🏆 2. Top 15 最常出现的 Secondary Words (拓展词)\n\n"
report += "| 拓展词 (Base Form) | 出现次数 |\n"
report += "| :--- | :--- |\n"
sorted_sec = sorted(secondary_word_freq.items(), key=lambda x: x[1], reverse=True)
for word, count in sorted_sec[:15]:
    report += f"| {word} | {count} |\n"
    
report += "\n## 📄 3. 各篇文章提取明细\n\n"
report += "| 文章 ID | 目标词 (Target Words) 注入数 | 拓展词 (Secondary Words) 注入数 |\n"
report += "| :--- | :--- | :--- |\n"
report += "\n".join(article_stats)
report += "\n"

with open("statistics_report.md", "w", encoding="utf-8") as f:
    f.write(report)

print("Statistics generated.")
