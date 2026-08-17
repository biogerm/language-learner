import json, re
with open('../SFI/web_app/data.js') as f:
    text = f.read()
json_str = re.sub(r"^const\s+APP_DATA\s*=\s*", "", text.strip())
if json_str.endswith(";"): json_str = json_str[:-1]
data = json.loads(json_str)
sfid = data.get("sfid", {})
stages = list(sfid.keys())
print("Stages:", stages[:5])
if stages:
    arts = list(sfid[stages[0]].keys())
    print("Articles in Stage 1:", arts[:5])
