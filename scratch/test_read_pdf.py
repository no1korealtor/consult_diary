import pypdf
import os
import sys

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

pdf_path1 = r"d:\부동산업무\antigravity\consult_diary\scratch\Korealtor배포용_260712_0728\배포\시세브리핑\시세브리핑_성산동_138.pdf"
pdf_path2 = r"d:\부동산업무\antigravity\consult_diary\scratch\시세브리핑\시세브리핑_성산동_138.pdf"

def print_pdf_content(path):
    print(f"\n======================================")
    print(f"Reading PDF: {path}")
    print(f"======================================")
    if not os.path.exists(path):
        print("File does not exist.")
        return
    reader = pypdf.PdfReader(path)
    for idx, page in enumerate(reader.pages):
        print(f"--- Page {idx+1} ---")
        text = page.extract_text()
        print(text)

print_pdf_content(pdf_path1)
print_pdf_content(pdf_path2)
