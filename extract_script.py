# -*- coding: utf-8 -*-
with open('rosary.html', 'rb') as f:
    text = f.read().decode('utf-8')

# Let's extract everything inside the main <script> tag
start_tag = "<script>"
end_tag = "</script>"
first_script_start = text.find(start_tag)
first_script_end = text.find(end_tag)

code = text[first_script_start + len(start_tag):first_script_end]

with open('test_syntax.js', 'wb') as f:
    f.write(code.encode('utf-8'))

print("Saved test_syntax.js, length:", len(code))
