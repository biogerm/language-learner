import urllib.request
import json
import os

prompt_text = open("prompts/eval_prompt.txt", "r", encoding="utf-8").read()

data = {
    "model": "claude-3-5-sonnet-20241022",  # Default model name can be anything, local router will handle it usually. We will use a generic one. Wait, let's use a standard one.
    "messages": [
        {"role": "user", "content": prompt_text}
    ],
    "temperature": 0.0
}

req = urllib.request.Request(
    "http://127.0.0.1:8787/v1/chat/completions", 
    data=json.dumps(data).encode("utf-8"),
    headers={"Content-Type": "application/json", "Authorization": "Bearer fake_key"}
)

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        print(result["choices"][0]["message"]["content"])
except Exception as e:
    print(f"Error calling local LLM: {e}")
