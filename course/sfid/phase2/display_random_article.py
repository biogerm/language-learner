import json
import random

def get_random_article():
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        course = json.load(f)
        
    all_articles = []
    for step in course["steps"]:
        for article in step["articles"]:
            all_articles.append((step["step_title"], article))
            
    if not all_articles:
        print("No articles found.")
        return
        
    theme, article = random.choice(all_articles)
    
    sentence_obj = article["sentences"][0]
    sv_text = sentence_obj["sv"]
    target_words = sentence_obj["target_words"]
    
    # Sort target words by start position in reverse order so that inserting formatting doesn't mess up subsequent indices
    target_words_sorted = sorted(target_words, key=lambda x: x["position_start"], reverse=True)
    
    formatted_sv = sv_text
    
    for word_info in target_words_sorted:
        start = word_info["position_start"]
        end = word_info["position_end"]
        
        # Double check if the index matches
        actual_word = formatted_sv[start:end]
        if actual_word == word_info["word_in_sentence"]:
            # Insert ** around the word
            formatted_sv = formatted_sv[:start] + "**" + actual_word + "**" + formatted_sv[end:]
        else:
            print(f"Warning: Index mismatch for '{word_info['word_in_sentence']}'. Found '{actual_word}' instead. Did not bold.")
            
    print(f"### Theme: {theme}")
    print(f"### Article ID: {article['article_id']}\n")
    print(formatted_sv)

if __name__ == "__main__":
    get_random_article()
