import json

with open("scratch/sungsan_villa_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Loaded {len(data)} items successfully.")
