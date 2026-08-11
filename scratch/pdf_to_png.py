import fitz
import os

pdf_path = os.path.join("시세브리핑", "시세브리핑_서울특별시_마포구_중동_395.pdf")
out_dir = "시세브리핑"

if os.path.exists(pdf_path):
    print(f"Opening {pdf_path}...")
    doc = fitz.open(pdf_path)
    for idx, page in enumerate(doc):
        pix = page.get_pixmap(dpi=150)
        out_name = f"page_{idx+1}.png"
        out_path = os.path.join(out_dir, out_name)
        pix.save(out_path)
        print(f"Saved {out_path}")
else:
    print(f"Error: {pdf_path} does not exist.")
