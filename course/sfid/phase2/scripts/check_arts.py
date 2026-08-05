import json

def check(f):
    with open(f, "r", encoding="utf-8") as file:
        data = json.load(file)
        print(f"{f}: {list(data.keys())}")

check("articles/article_9.json")
check("articles/article_10.json")
