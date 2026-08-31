import json
import os
import re

def process():
    data_path = "../SFI/web_app/data.js"
    with open(data_path, 'r', encoding='utf-8') as f:
        content = f.read()

    start_idx = content.find('{')
    end_idx = content.rfind('}')
    json_str = content[start_idx:end_idx+1]
    app_data = json.loads(json_str)
    sfid_data = app_data.get('sfid', {})
    
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='sv'>")
    html.append("<head>")
    html.append("<meta charset='UTF-8'>")
    html.append("<title>SFID B1 Articles</title>")
    html.append("<style>")
    html.append("""
        @media print {
            @page { size: A4; margin: 2.5cm; }
            body { 
                background: transparent !important; 
                max-width: 100% !important; 
                padding: 0 !important;
                margin: 0 !important;
            }
            h2 { page-break-after: avoid; }
            .article { page-break-inside: auto; }
            .chunk { page-break-inside: auto; }
            .sv-text, .en-text { page-break-inside: auto; orphans: 3; widows: 3; }
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #111;
            background: #fff;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .article { margin-bottom: 60px; }
        h2 { 
            font-size: 20px; 
            border-bottom: 1px solid #ddd; 
            padding-bottom: 8px;
            margin-bottom: 20px;
            color: #333;
        }
        .chunk {
            margin-bottom: 30px;
        }
        .sv-text {
            font-size: 16px;
            line-height: 1.8;
            letter-spacing: 0.2px;
            margin-bottom: 8px;
            text-align: justify;
        }
        .en-text {
            font-size: 15px;
            line-height: 1.6;
            color: #555;
            text-align: justify;
            margin-top: 0;
            padding-left: 15px;
            border-left: 3px solid #eee;
        }
        .target-word {
            color: #2563eb;
            font-weight: 600;
        }
        .secondary-word {
            color: inherit;
            text-decoration: underline;
            text-decoration-color: #94a3b8;
            text-underline-offset: 3px;
        }
    """)
    html.append("</style>")
    html.append("</head>")
    html.append("<body>")

    article_count = 0
    for stage_name, articles in sfid_data.items():
        for article_title, sentences in articles.items():
            if not sentences:
                continue
            article_count += 1
            html.append(f"<div class='article'>")
            html.append(f"<h2>{stage_name} - {article_title}</h2>")
            
            sv_chunk = []
            en_chunk = []
            chunk_char_count = 0
            
            for idx, sentence_obj in enumerate(sentences):
                sv_text = sentence_obj.get("sv", "")
                en_text = sentence_obj.get("en", "")
                target_words = sentence_obj.get("target_words", [])
                secondary_words = sentence_obj.get("secondary_words", [])
                
                # --- SWEDISH HIGHLIGHTING ---
                is_bold = [False] * len(sv_text)
                is_under = [False] * len(sv_text)
                
                for tw in target_words:
                    if isinstance(tw, dict):
                        start = tw.get("position_start")
                        end = tw.get("position_end")
                        if start is not None and end is not None:
                            for i in range(start, min(end, len(is_bold))):
                                is_bold[i] = True
                        elif "word" in tw:
                            word = tw["word"]
                            pos = sv_text.find(word)
                            if pos != -1:
                                for i in range(pos, min(pos + len(word), len(is_bold))):
                                    is_bold[i] = True
                    elif isinstance(tw, str):
                        pos = sv_text.find(tw)
                        if pos != -1:
                            for i in range(pos, min(pos + len(tw), len(is_bold))):
                                is_bold[i] = True
                
                for sw in secondary_words:
                    if isinstance(sw, dict):
                        start = sw.get("position_start")
                        end = sw.get("position_end")
                        if start is not None and end is not None:
                            for i in range(start, min(end, len(is_under))):
                                is_under[i] = True
                        elif "word" in sw:
                            word = sw["word"]
                            pos = sv_text.find(word)
                            if pos != -1:
                                for i in range(pos, min(pos + len(word), len(is_under))):
                                    is_under[i] = True
                    elif isinstance(sw, str):
                        pos = sv_text.find(sw)
                        if pos != -1:
                            for i in range(pos, min(pos + len(sw), len(is_under))):
                                is_under[i] = True
                                
                html_chars = []
                prev_state = (False, False)

                for i, char in enumerate(sv_text):
                    curr_state = (is_bold[i], is_under[i])
                    if curr_state != prev_state:
                        if prev_state == (True, True):
                            html_chars.append("</span></span>")
                        elif prev_state == (True, False) or prev_state == (False, True):
                            html_chars.append("</span>")
                            
                        if curr_state == (True, True):
                            html_chars.append("<span class='target-word'><span class='secondary-word'>")
                        elif curr_state == (True, False):
                            html_chars.append("<span class='target-word'>")
                        elif curr_state == (False, True):
                            html_chars.append("<span class='secondary-word'>")
                            
                        prev_state = curr_state
                        
                    html_chars.append(char)

                if prev_state == (True, True):
                    html_chars.append("</span></span>")
                elif prev_state == (True, False) or prev_state == (False, True):
                    html_chars.append("</span>")
                    
                sv_html = "".join(html_chars)
                sv_html = sv_html.replace("\\n", "<br>").replace("\n", "<br>")
                sv_chunk.append(sv_html)
                chunk_char_count += len(sv_text)

                # --- ENGLISH HIGHLIGHTING ---
                if en_text:
                    all_words = []
                    for tw in target_words:
                        if isinstance(tw, dict) and tw.get("contextual_en"):
                            all_words.append({"en": tw["contextual_en"], "type": "target-word"})
                    for sw in secondary_words:
                        if isinstance(sw, dict) and sw.get("contextual_en"):
                            all_words.append({"en": sw["contextual_en"], "type": "secondary-word"})
                    
                    all_words.sort(key=lambda x: len(x["en"]), reverse=True)
                    
                    tokens = []
                    for w_idx, w in enumerate(all_words):
                        escaped = re.escape(w["en"])
                        pattern = r'\b' + escaped + r'\b'
                        if not re.search(pattern, en_text, re.IGNORECASE):
                            pattern = escaped
                        
                        match = re.search(pattern, en_text, re.IGNORECASE)
                        if match:
                            token = f"__TOKEN_{w_idx}__"
                            tokens.append((token, f"<span class='{w['type']}'>{match.group(0)}</span>"))
                            en_text = re.sub(pattern, token, en_text, count=1, flags=re.IGNORECASE)
                    
                    for token, html_str in tokens:
                        en_text = en_text.replace(token, html_str)
                    
                    en_html = en_text.replace("\\n", "<br>").replace("\n", "<br>")
                    en_chunk.append(en_html)

                # Output chunk if it exceeds ~350 characters or it's the last sentence
                if chunk_char_count >= 350 or idx == len(sentences) - 1:
                    html.append("<div class='chunk'>")
                    html.append(f"<p class='sv-text'>{' '.join(sv_chunk)}</p>")
                    if any(en_chunk):
                        html.append(f"<p class='en-text'>{' '.join(filter(None, en_chunk))}</p>")
                    html.append("</div>")
                    
                    sv_chunk = []
                    en_chunk = []
                    chunk_char_count = 0
                    
            html.append("</div>") # End article

    html.append("</body>")
    html.append("</html>")
    
    out_dir = "course/sfid/phase5/output"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "sfid_b1_articles.html")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(html))
        
    print(f"Generated {out_path} with {article_count} articles.")

if __name__ == '__main__':
    process()
