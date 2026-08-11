import unittest
from unittest.mock import patch, MagicMock
import urllib.error
import io
import sys

# Import functions to test
from trade_viewer import (
    parse_address_and_ho,
    classify_property_type,
    format_price,
    print_comparison_table,
    get_recent_transactions
)

class TestTradeViewer(unittest.TestCase):

    def test_parse_address_and_ho(self):
        """Test address parsing logic with room numbers (호) and dongs (동)"""
        # Case 1: Room specified with "호"
        addr, dong, ho = parse_address_and_ho("서울 마포구 성산동 138 402호")
        self.assertEqual(addr, "서울 마포구 성산동 138")
        self.assertEqual(dong, "")
        self.assertEqual(ho, "402")
 
        # Case 2: Room specified without "호" at the end of address
        addr, dong, ho = parse_address_and_ho("서울 마포구 성산동 138 402")
        self.assertEqual(addr, "서울 마포구 성산동 138")
        self.assertEqual(dong, "")
        self.assertEqual(ho, "402")
 
        # Case 3: No room number
        addr, dong, ho = parse_address_and_ho("서울 마포구 성산동 200-94")
        self.assertEqual(addr, "서울 마포구 성산동 200-94")
        self.assertEqual(dong, "")
        self.assertEqual(ho, "")

        # Case 4: Dong and Room specified (e.g. 102동 101호)
        addr, dong, ho = parse_address_and_ho("중동 395 102동 101호")
        self.assertEqual(addr, "중동 395")
        self.assertEqual(dong, "102")
        self.assertEqual(ho, "101")

        # Case 5: Dong and Room specified with dash (e.g. 102-101)
        addr, dong, ho = parse_address_and_ho("중동 395 102-101")
        self.assertEqual(addr, "중동 395")
        self.assertEqual(dong, "102")
        self.assertEqual(ho, "101")

    def test_classify_property_type(self):
        """Test property type classification logic"""
        # Apartment
        self.assertEqual(classify_property_type("아파트", "현대아파트"), "1")
        # Officetel
        self.assertEqual(classify_property_type("업무시설", "마포오피스텔"), "3")
        # Villa/Rowhouse
        self.assertEqual(classify_property_type("공동주택", "성산빌라"), "2")
        # General/Single house
        self.assertEqual(classify_property_type("단독주택", "단독"), "4")
        # Default fallback
        self.assertEqual(classify_property_type("", ""), "2")

    def test_format_price_trade(self):
        """Test formatting of trade amounts"""
        item = {'dealAmount': '125,000'}
        display, amt, rent = format_price(item, is_rent=False)
        self.assertEqual(display, "12억 5,000만")
        self.assertEqual(amt, 125000)
        self.assertIsNone(rent)

        item_under_eok = {'dealAmount': '8,500'}
        display, amt, rent = format_price(item_under_eok, is_rent=False)
        self.assertEqual(display, "8,500만")
        self.assertEqual(amt, 8500)

    def test_format_price_rent(self):
        """Test formatting of rental (Jeonse/Wolse) amounts"""
        # Jeonse
        item_jeonse = {'deposit': '35,000', 'monthlyRent': '0'}
        display, dep, rent = format_price(item_jeonse, is_rent=True)
        self.assertEqual(display, "3억 5,000만")
        self.assertEqual(dep, 35000)
        self.assertEqual(rent, 0)

        # Wolse
        item_wolse = {'deposit': '5,000', 'monthlyRent': '80'}
        display, dep, rent = format_price(item_wolse, is_rent=True)
        self.assertEqual(display, "5,000만/80만")
        self.assertEqual(dep, 5000)
        self.assertEqual(rent, 80)

    @patch('urllib.request.urlopen')
    def test_get_recent_transactions_success(self, mock_urlopen):
        """Test successful fetch of transactions (returning mock JSON) with dong filtering"""
        def urlopen_side_effect(req, *args, **kwargs):
            url = req.full_url if hasattr(req, 'full_url') else str(req)
            mock_resp = MagicMock()
            if 'Trade' in url:
                mock_resp.read.return_value = '{"response": {"header": {"resultCode": "00"}, "body": {"items": {"item": [{"dealYear": 2026, "dealMonth": 6, "dealDay": 10, "jibun": "200-94", "dealAmount": "35,000", "umdNm": "성산동"}]}}}}'.encode('utf-8')
            else:
                mock_resp.read.return_value = '{"response": {"header": {"resultCode": "00"}, "body": {"items": {"item": [{"dealYear": 2026, "dealMonth": 6, "dealDay": 12, "jibun": "200-94", "deposit": "25,000", "monthlyRent": "0", "umdNm": "성산동"}]}}}}'.encode('utf-8')
            return MagicMock(__enter__=MagicMock(return_value=mock_resp))

        mock_urlopen.side_effect = urlopen_side_effect

        # 1. Execute without bjdong_nm filter
        transactions = get_recent_transactions("11440", "200", "94", "4")
        self.assertIsNotNone(transactions)
        self.assertTrue(len(transactions) > 0)
        self.assertEqual(transactions[0]['_trade_type'], '전세')
        self.assertEqual(transactions[0]['deposit'], '25,000')
        trade_items = [t for t in transactions if t['_trade_type'] == '매매']
        self.assertTrue(len(trade_items) > 0)
        self.assertEqual(trade_items[0]['dealAmount'], '35,000')

        # 2. Execute with matching bjdong_nm filter
        transactions_match = get_recent_transactions("11440", "200", "94", "4", "성산동")
        self.assertEqual(len(transactions_match), 48) # 24 months * 2 items

        # 3. Execute with non-matching bjdong_nm filter
        transactions_mismatch = get_recent_transactions("11440", "200", "94", "4", "중동")
        self.assertEqual(len(transactions_mismatch), 0)

    @patch('urllib.request.urlopen')
    def test_get_recent_transactions_403_forbidden(self, mock_urlopen):
        """Test 403 Forbidden error handling"""
        # Setup mock HTTPError
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="http://apis.data.go.kr/...",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=None
        )

        # Suppress prints during test
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            transactions = get_recent_transactions("11440", "200", "94", "4")
        finally:
            sys.stdout = sys.__stdout__

        # Verify
        self.assertIsNone(transactions)
        # Check that error guide was printed
        self.assertIn("공공데이터 API 호출 오류 (인증 실패 / 403 Forbidden)", captured_output.getvalue())

    @patch('urllib.request.urlopen')
    def test_get_recent_transactions_empty(self, mock_urlopen):
        """Test empty results response (resultCode 00 but no items)"""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"response": {"header": {"resultCode": "00"}, "body": {"items": ""}}}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        transactions = get_recent_transactions("11440", "200", "94", "4")
        
    @patch('urllib.request.urlopen')
    def test_get_recent_transactions_partial_403(self, mock_urlopen):
        """Test partial 403 Forbidden error handling (trade fails, rent succeeds)"""
        def urlopen_side_effect(req, *args, **kwargs):
            url = req.full_url if hasattr(req, 'full_url') else str(req)
            if 'Trade' in url:
                raise urllib.error.HTTPError(
                    url=url,
                    code=403,
                    msg="Forbidden",
                    hdrs=None,
                    fp=None
                )
            else:
                mock_resp = MagicMock()
                mock_resp.read.return_value = b'{"response": {"header": {"resultCode": "00"}, "body": {"items": {"item": [{"dealYear": 2026, "dealMonth": 6, "dealDay": 12, "jibun": "200-94", "deposit": "25,000", "monthlyRent": "0"}]}}}}'
                return MagicMock(__enter__=MagicMock(return_value=mock_resp))

        mock_urlopen.side_effect = urlopen_side_effect

        # Suppress prints during test
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            transactions = get_recent_transactions("11440", "200", "94", "4")
        finally:
            sys.stdout = sys.__stdout__

        # Verify
        self.assertIsNotNone(transactions)
        self.assertTrue(getattr(transactions, 'trade_permission_error', False))
        self.assertFalse(getattr(transactions, 'rent_permission_error', False))
        # Check that partial error guide was printed
        self.assertIn("일부 실거래 API 호출 오류 (인증 실패 / 403 Forbidden)", captured_output.getvalue())
        self.assertEqual(len(transactions), 24) # rent succeeds for all 24 months

    @patch('builtins.input')
    @patch('trade_viewer.get_recent_transactions')
    @patch('trade_viewer.save_briefing_report')
    def test_print_comparison_table_expand_yes(self, mock_save, mock_get_recent, mock_input):
        """Test that print_comparison_table offers and performs similarity-based expansion"""
        # 1. Setup mock transactions with low data count (e.g. 1 transaction)
        initial_transactions = [
            {"dealYear": 2026, "dealMonth": 6, "dealDay": 12, "jibun": "200-94", "excluUseAr": 35.5, "_trade_type": "매매", "dealAmount": "35,000"}
        ]
        # 2. Setup mock expanded transactions
        expanded_transactions = [
            {"dealYear": 2026, "dealMonth": 6, "dealDay": 12, "jibun": "200-94", "excluUseAr": 35.5, "_trade_type": "매매", "dealAmount": "35,000"},
            {"dealYear": 2026, "dealMonth": 5, "dealDay": 10, "jibun": "200-95", "excluUseAr": 34.0, "_trade_type": "매매", "dealAmount": "33,000"},
            {"dealYear": 2026, "dealMonth": 4, "dealDay": 8, "jibun": "200-96", "excluUseAr": 37.0, "_trade_type": "매매", "dealAmount": "38,000"}
        ]
        
        mock_get_recent.return_value = expanded_transactions
        mock_input.side_effect = ['1', '2'] # '1' for strict expansion, '2' for period analysis prompt (12 months)
        
        # Suppress prints during test
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            print_comparison_table(
                transactions=initial_transactions,
                prop_type="2",
                target_floor=3,
                target_area=35.5,
                address_name="서울특별시 마포구 성산동 200-94",
                sigunguCd="11440",
                bun="200",
                ji="94",
                bjdong_nm="성산동",
                target_build_year=2015
            )
        finally:
            sys.stdout = sys.__stdout__
            
        # Verify that get_recent_transactions was called with expand_similar=True and margins
        mock_get_recent.assert_called_once_with(
            "11440", "200", "94", "2", "성산동",
            target_build_year=2015,
            target_house_type=None,
            expand_similar=True,
            target_area=35.5,
            build_year_margin=3,
            area_margin=0.15
        )
        
        # Verify that save_briefing_report was called with is_expanded=True
        mock_save.assert_called_once()
        args, kwargs = mock_save.call_args
        self.assertEqual(args[6], True)
        self.assertEqual(args[7], 2015)
        self.assertEqual(args[8], 35.5)

if __name__ == '__main__':
    unittest.main()
