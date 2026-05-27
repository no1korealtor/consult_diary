import re
import sys

filepath = r"c:\Users\USER\OneDrive\바탕 화면\조항준\reuni.kr 백업 20260526\dbno1korealtor_20260526112829.sql\dbno1korealtor.sql"

found_create = False
create_lines = []
insert_lines = []

try:
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.lower().startswith('create table') and 'article_tbl' in line.lower():
                found_create = True
            
            if found_create:
                create_lines.append(line.strip())
                if ';' in line:
                    found_create = False

            if line.lower().startswith('insert into') and 'article_tbl' in line.lower():
                insert_lines.append(line[:500] + '...')
                if len(insert_lines) > 2:
                    break
                    
except Exception as e:
    print(f"Error: {e}")

print("--- CREATE TABLE ---")
print('\n'.join(create_lines))
print("--- INSERT INTO ---")
print('\n'.join(insert_lines))
