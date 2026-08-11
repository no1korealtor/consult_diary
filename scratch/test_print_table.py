import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from trade_viewer import print_comparison_table

def test_mock_print():
    mock_trades = [
        # 매매
        {
            '_trade_type': '매매',
            'dealYear': 2025, 'dealMonth': 10, 'dealDay': 1,
            'dealAmount': '30,000', 'excluUseAr': '59.84', 'landAr': '33.86',
            'floor': '1', 'aptDong': '101'
        },
        {
            '_trade_type': '매매',
            'dealYear': 2025, 'dealMonth': 11, 'dealDay': 10,
            'dealAmount': '35,000', 'excluUseAr': '59.84', 'landAr': '33.86',
            'floor': '2', 'aptDong': '101'
        },
        # 전세
        {
            '_trade_type': '전세',
            'dealYear': 2025, 'dealMonth': 10, 'dealDay': 5,
            'deposit': '20,000', 'excluUseAr': '59.84', 'landAr': '33.86',
            'floor': '2', 'aptDong': '101'
        },
        {
            '_trade_type': '전세',
            'dealYear': 2025, 'dealMonth': 11, 'dealDay': 15,
            'deposit': '22,000', 'excluUseAr': '59.84', 'landAr': '33.86',
            'floor': '3', 'aptDong': '101'
        },
        # 월세
        {
            '_trade_type': '월세',
            'dealYear': 2025, 'dealMonth': 10, 'dealDay': 12,
            'deposit': '3,000', 'monthlyRent': '80', 'excluUseAr': '59.84', 'landAr': '33.86',
            'floor': '1', 'aptDong': '101'
        },
        {
            '_trade_type': '월세',
            'dealYear': 2025, 'dealMonth': 11, 'dealDay': 22,
            'deposit': '5,000', 'monthlyRent': '90', 'excluUseAr': '59.84', 'landAr': '33.86',
            'floor': '2', 'aptDong': '101'
        }
    ]
    
    print("\n" + "="*50)
    print("MOCK ALL TYPES COMPARISON TABLE TEST")
    print("="*50)
    
    print_comparison_table(mock_trades, prop_type='2')

if __name__ == "__main__":
    test_mock_print()
