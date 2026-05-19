import os
import glob

replacements = {
    "from('deals')": "from('schedules')",
    'from("deals")': 'from("schedules")',
    "from('deal_attendances')": "from('schedule_attendances')",
    'from("deal_attendances")': 'from("schedule_attendances")',
    "contract_type": "schedule_type",
    "balance_date": "schedule_date",
    "deal_id": "schedule_id",
    "dealId": "scheduleId",  # Common variable name
    "deal.": "schedule.",
    "deals (": "schedules (",
    "deals(": "schedules(",
}

files_to_check = glob.glob("*.html") + glob.glob("*.js")

for filepath in files_to_check:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for old, new in replacements.items():
        new_content = new_content.replace(old, new)
        
    if new_content != content:
        print(f"Updated {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

print("Done")
