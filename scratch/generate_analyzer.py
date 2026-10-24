import json

# Load data
with open("scratch/sungsan_villa_data.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

print(f"Loaded {len(raw_data)} records.")
