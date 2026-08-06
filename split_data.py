import json

with open('parsed_discrepancies.json', 'r') as f:
    data = json.load(f)

chunk_size = len(data) // 5 + 1
for i in range(5):
    chunk = data[i*chunk_size : (i+1)*chunk_size]
    with open(f'chunk_{i}.json', 'w') as f:
        json.dump(chunk, f, indent=2)
print("Chunks created.")
