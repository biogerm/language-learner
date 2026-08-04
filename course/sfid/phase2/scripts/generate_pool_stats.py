import json
import math

def main():
    with open("clustered_dictionary.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    abstract_words = data.get("Abstrakta Koncept", [])
    specific_themes = {k: v for k, v in data.items() if k != "Abstrakta Koncept"}
    
    total_concrete = sum(len(v) for v in specific_themes.values())
    total_abstract = len(abstract_words)
    
    allocated_abstract = 0
    stats = []
    
    # Sort themes by concrete count descending for nicer display
    sorted_themes = sorted(specific_themes.items(), key=lambda x: len(x[1]), reverse=True)
    
    for idx, (theme, words) in enumerate(sorted_themes):
        concrete_count = len(words)
        
        if idx == len(sorted_themes) - 1:
            abs_count = total_abstract - allocated_abstract
        else:
            abs_count = round(concrete_count * (total_abstract / total_concrete))
            allocated_abstract += abs_count
            
        total_pool = concrete_count + abs_count
        articles = round(total_pool / 50)
        
        stats.append({
            "theme": theme,
            "concrete": concrete_count,
            "abstract": abs_count,
            "total": total_pool,
            "articles": max(1, articles)
        })
        
    print(f"{'Theme':<25} | {'Concrete':<9} | {'Abstract':<9} | {'Total':<6} | {'Articles'}")
    print("-" * 70)
    total_arts = 0
    for s in stats:
        print(f"{s['theme'][:24]:<25} | {s['concrete']:<9} | {s['abstract']:<9} | {s['total']:<6} | {s['articles']}")
        total_arts += s['articles']
        
    print("-" * 70)
    print(f"{'TOTAL':<25} | {total_concrete:<9} | {total_abstract:<9} | {total_concrete+total_abstract:<6} | {total_arts}")

if __name__ == "__main__":
    main()
