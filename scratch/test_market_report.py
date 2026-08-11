import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from market_analyser import generate_market_report_pdf, load_member_info

member_info = load_member_info()

pdf_filename = "test_market_report.pdf"
generate_market_report_pdf(
    pdf_filename=pdf_filename,
    bjdong_nm="성산동",
    apt_txs=[],
    villa_txs=[],
    member_info=member_info,
    region_prefix="서울특별시 마포구"
)
print("Generated PDF:", os.path.abspath(pdf_filename))
