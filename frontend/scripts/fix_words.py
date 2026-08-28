import json

with open('public/courses/sfid/course_sfid_articles.json', 'r') as f:
    data = json.load(f)

for stage in data['stages']:
    if stage['stage_title'] == 'Blandade Meningar':
        for article in stage['articles']:
            if article.get('article_id') == 'art_58':
                for sentence in article['sentences']:
                    if 'words' in sentence:
                        sentence['target_words'] = sentence.pop('words')

with open('public/courses/sfid/course_sfid_articles.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
