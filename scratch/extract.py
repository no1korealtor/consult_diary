import os

log_path = r'C:\Users\USER\.gemini\antigravity\brain\f7c5868b-bc9f-415e-9b9f-d566ddf80a1a\.system_generated\logs\overview.txt'
with open(log_path, 'r', encoding='utf-8') as f:
    text = f.read()

start = text.rfind('The following code has been modified to include a line number before every line')
if start != -1:
    end = text.find('The above content does NOT show the entire file', start)
    if end != -1:
        print(text[start:end])
