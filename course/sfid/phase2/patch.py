import sys
with open("orchestrator.py", "r") as f:
    code = f.read()
code = code.replace("""    try:
        art_node = article_data["steps"][0]["articles"][0]
        used_words = set(art_node.get("primary_words_used", []))
    except KeyError:
        print("Error: Invalid JSON architecture.")
        sys.exit(1)""", """    try:
        # Check if nested or flat
        if "steps" in article_data:
            art_node = article_data["steps"][0]["articles"][0]
        else:
            art_node = article_data
        used_words = set(art_node.get("primary_words_used", []))
    except KeyError:
        print("Error: Invalid JSON architecture.")
        sys.exit(1)""")
with open("orchestrator.py", "w") as f:
    f.write(code)
