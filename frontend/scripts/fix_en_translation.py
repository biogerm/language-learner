import json

with open('public/courses/sfid/course_sfid_articles.json', 'r') as f:
    data = json.load(f)

for stage in data['stages']:
    if stage['stage_title'] == 'Blandade Meningar':
        for article in stage['articles']:
            if article.get('article_id') == 'art_58':
                for sentence in article['sentences']:
                    for word_list_key in ['target_words', 'secondary_words']:
                        if word_list_key in sentence:
                            for word in sentence[word_list_key]:
                                if 'en_translation' in word:
                                    word['contextual_en'] = word.pop('en_translation')

with open('public/courses/sfid/course_sfid_articles.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
