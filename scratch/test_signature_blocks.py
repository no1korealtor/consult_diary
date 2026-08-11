import sys
import os
import json
import unittest

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestSignatureBlocks(unittest.TestCase):
    def test_member_info_registration_number(self):
        # 1. Assert member_info.json has registration number
        from market_analyser import load_member_info
        member_info = load_member_info()
        self.assertEqual(member_info.get("registration_number"), "92380000-4131")

    def test_market_analyser_signature_labels(self):
        # 2. Check market_analyser.py source file content for updated labels
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "market_analyser.py")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("중개의뢰 및 문의", content)
        self.assertIn("등록번호", content)
        self.assertIn("SPAN", content)

    def test_trade_viewer_registration_number(self):
        # 3. Check trade_viewer.py handles registration number
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trade_viewer.py")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("registration_number", content)

if __name__ == '__main__':
    unittest.main()
