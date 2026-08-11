import unittest
from unittest.mock import patch, MagicMock
import json
import get_building_info as gb

class TestBuildingInfo(unittest.TestCase):

    @patch('urllib.request.urlopen')
    def test_get_building_data_normal(self, mock_urlopen):
        # 정상적인 정부 API 응답 모의(Mock)
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "response": {
                "header": {"resultCode": "00"},
                "body": {
                    "items": {
                        "item": [
                            {
                                "totArea": 233.58,
                                "platArea": 150.0,
                                "archArea": 77.86,
                                "grndFlrCnt": 2,
                                "ugrndFlrCnt": 1,
                                "hhldCnt": 0,
                                "fmlyCnt": 5,
                                "violBldYn": "Y"
                            }
                        ]
                    }
                }
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        res = gb.get_building_data('11440', '12500', '0200', '0094')
        self.assertIsNotNone(res)
        self.assertEqual(res['totArea'], '233.58')
        self.assertEqual(res['households'], '5')
        self.assertEqual(res['violBldYn'], 'Y')

    @patch('urllib.request.urlopen')
    def test_get_building_data_missing_viol(self, mock_urlopen):
        # 성산동 200-94처럼 violBldYn 항목이 아예 누락된 응답 모의
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "response": {
                "header": {"resultCode": "00"},
                "body": {
                    "items": {
                        "item": [
                            {
                                "totArea": 100.0,
                                "grndFlrCnt": 1
                                # violBldYn 없음!
                            }
                        ]
                    }
                }
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        res = gb.get_building_data('11110', '11111', '0123', '0123')
        self.assertIsNotNone(res)
        # 현재 로직은 누락 시 'N'으로 치환하도록 되어 있는데, 이 정책이 맞는지 테스트
        self.assertEqual(res['violBldYn'], 'N')

    @patch('urllib.request.urlopen')
    def test_get_building_data_empty_response(self, mock_urlopen):
        # 서버 점검 등으로 빈 응답이 올 때 죽지 않는지 테스트
        mock_response = MagicMock()
        mock_response.read.return_value = b""
        mock_urlopen.return_value.__enter__.return_value = mock_response

        res = gb.get_building_data('11110', '11111', '0123', '0123')
        self.assertIsNone(res)

if __name__ == '__main__':
    unittest.main()
