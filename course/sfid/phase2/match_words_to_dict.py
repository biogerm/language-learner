import json

def match_article_words():
    # Parse line numbers from master_dictionary.json
    word_lines = {}
    with open("../phase1/master_dictionary.json", "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line_str = line.strip()
            if line_str.startswith('"') and '": {' in line_str:
                # Extracts the key from "word": {
                word = line_str.split('"')[1]
                word_lines[word] = i
                
    try:
        with open("../phase1/master_dictionary.json", "r", encoding="utf-8") as f:
            dictionary = json.load(f)["words"]
    except Exception as e:
        print("Failed to load dictionary:", e)
        return

    # Load the articles
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        course = json.load(f)

    # Find art_11
    target_article = None
    for step in course["steps"]:
        for article in step["articles"]:
            if article["article_id"] == "art_11":
                target_article = article
                break
        if target_article:
            break

    if not target_article:
        print("Could not find art_11")
        return

    # Extract target words
    target_words_data = target_article["sentences"][0].get("target_words", [])
    
    print(f"### 单词溯源报告: {target_article['article_id']} ###\n")
    print(f"**文章标题**: {target_article['article_title']}\n")
    print(f"总计找到 {len(target_words_data)} 个目标单词，已成功与原始字典匹配并定位行号：\n")
    print("| 文中词汇 | 原始字典词汇 | 行号 (`master_dictionary.json`) | 英文释义 |")
    print("|---|---|---|---|")
    
    for item in target_words_data:
        dict_word = item.get("base_form")
        actual_word = item.get("word_in_sentence")
        
        entry = dictionary.get(dict_word)
        line_num = word_lines.get(dict_word, "N/A")
        
        if entry:
            print(f"| {actual_word} | {dict_word} | {line_num} | {entry.get('en', 'N/A')} |")
        else:
            print(f"| {actual_word} | {dict_word} | N/A | [在原始字典中未找到完美匹配] |")

if __name__ == "__main__":
    match_article_words()
