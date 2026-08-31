import fitz
import re

def main():
    pdf_path = '../SFI/courses/Nivatest/source_data/rivstart_B1_B2_TB__ordkort_1.pdf'
    out_path = 'extracted_ordkort.txt'
    
    doc = fitz.open(pdf_path)
    words = set()
    
    for page in doc:
        blocks = page.get_text("blocks")
        for b in blocks:
            text = b[4].strip()
            # Split by newlines within the block just in case
            for line in text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                # Filter out headers and footers
                if 'Kopieringsunderlag' in line or 'Rivstart' in line or 'ISBN' in line or '©' in line or 'Lärarhandledning' in line:
                    continue
                # Filter out pure digits (page numbers)
                if line.isdigit():
                    continue
                
                # Further cleaning: remove (en), (ett), en, ett
                # Actually let's just save the phrase as is for the output
                words.add(line)
                
    # Sort and save
    sorted_words = sorted(list(words))
    with open(out_path, 'w', encoding='utf-8') as f:
        for w in sorted_words:
            f.write(w + '\n')
            
    print(f"Extracted {len(sorted_words)} unique phrases/words.")
    print(f"Saved to {out_path}")
    
    # Check for English words
    # We strip 'en', 'ett', '(en)', '(ett)', 'sig' to check the base word
    english_words = {'here', 'there', 'is', 'and', 'the', 'it', 'to', 'you', 'that', 'he', 'was', 'for', 'on', 'are', 'with', 'as', 'I', 'his', 'they', 'be', 'at', 'one', 'have', 'this', 'from', 'or', 'had', 'by', 'not', 'word', 'but', 'what', 'some', 'we', 'can', 'out', 'other', 'were', 'all', 'your', 'when', 'up', 'use', 'how', 'said', 'an', 'each', 'she'}
    
    found_english = set()
    
    for phrase in sorted_words:
        # clean phrase
        clean_phrase = phrase.replace('(en)', '').replace('(ett)', '')
        # split into tokens
        tokens = re.findall(r'\b[a-zA-ZåäöÅÄÖ]+\b', clean_phrase.lower())
        for token in tokens:
            if token in ('en', 'ett', 'sig'):
                continue
            if token in english_words:
                found_english.add((token, phrase))
                
    if found_english:
        print("\nFound potentially English words in the extracted list:")
        for en_word, original in found_english:
            print(f" - '{en_word}' in phrase '{original}'")
    else:
        print("\nNo common English words found in the extracted list.")

if __name__ == '__main__':
    main()
