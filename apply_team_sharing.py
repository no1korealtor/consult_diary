import os
import re

directory = r"d:\부동산업무\antigravity\consult_diary"

for root, dirs, files in os.walk(directory):
    if 'api' in root or 'ediary' in root or '.git' in root or 'temp' in root:
        continue
    for file in files:
        if file.endswith('.html') or file.endswith('.js'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                new_content = content
                
                # 1. Fetching logic: change filter from user_id to office_id
                new_content = re.sub(
                    r"\.eq\(\s*['\"]user_id['\"]\s*,\s*window\.currentUser\.id\s*\)",
                    r".eq('office_id', window.currentUser.office_id)",
                    new_content
                )

                # 2. Inserting logic: append office_id to inserts
                # This regex looks for user_id: window.currentUser.id but avoids replacing it if office_id is already there
                # We use a simple replace because it's safe.
                if 'office_id: window.currentUser.office_id' not in new_content:
                    new_content = re.sub(
                        r"user_id\s*:\s*window\.currentUser\.id(?!, office_id)",
                        r"user_id: window.currentUser.id, office_id: window.currentUser.office_id",
                        new_content
                    )
                
                # 3. Ownership check logic: allow brokers to bypass isMine
                new_content = re.sub(
                    r"const isMine = (.*?) === window\.currentUser\.id;",
                    r"const isMine = \1 === window.currentUser.id || window.currentUser.role === 'broker';",
                    new_content
                )

                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated {filepath}")
            except Exception as e:
                print(f"Failed to process {filepath}: {e}")
