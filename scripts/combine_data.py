import json

# Read the three JSON files
with open('ai-engr1-data.json', 'r', encoding='utf-8') as f:
    data1 = json.load(f)

with open('ai-engr2-data.json', 'r', encoding='utf-8') as f:
    data2 = json.load(f)

with open('ai-engr3-data.json', 'r', encoding='utf-8') as f:
    data3 = json.load(f)

# Combine all data into a single dictionary
combined_data = {}

# Add items from first file (1-50)
for key, value in data1.items():
    combined_data[key] = value

# Add items from second file (51-100)
offset = 50
for key, value in data2.items():
    new_key = str(int(key) + offset)
    combined_data[new_key] = value

# Add items from third file (101-150)
offset = 100
for key, value in data3.items():
    new_key = str(int(key) + offset)
    combined_data[new_key] = value

# Write the combined data to a new file
with open('ai-engr.json', 'w', encoding='utf-8') as f:
    json.dump(combined_data, f, indent=2, ensure_ascii=False)

print(f"Successfully combined {len(combined_data)} items into ai-engr.json")
print(f"Items from ai-engr1-data.json: {len(data1)}")
print(f"Items from ai-engr2-data.json: {len(data2)}")
print(f"Items from ai-engr3-data.json: {len(data3)}")
