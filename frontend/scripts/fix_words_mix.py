import json

with open('public/courses/sfid/course_sfid_articles.json', 'r') as f:
    data = json.load(f)

for stage in data['stages']:
    if stage['stage_title'] == 'Blandade Meningar':
        for article in stage['articles']:
            if article.get('article_id') == 'art_58':
                
                # Sentence 1: "Detta är den första testmeningen."
                s1 = article['sentences'][0]
                all_words_1 = s1.get('target_words', []) + s1.get('words', [])
                s1['target_words'] = [w for w in all_words_1 if w['base_form'] in ['första', 'testmening']]
                s1['secondary_words'] = [w for w in all_words_1 if w['base_form'] in ['detta']]
                # The rest are dropped, so they become unhighlighted text.
                
                # Sentence 2: "Här kommer en andra mening för att testa."
                s2 = article['sentences'][1]
                all_words_2 = s2.get('target_words', []) + s2.get('words', [])
                s2['target_words'] = [w for w in all_words_2 if w['base_form'] in ['andra', 'testa']]
                s2['secondary_words'] = [w for w in all_words_2 if w['base_form'] in ['mening']]
                
                # Make sure to remove 'words' if it existed
                if 'words' in s1: del s1['words']
                if 'words' in s2: del s2['words']

with open('public/courses/sfid/course_sfid_articles.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
