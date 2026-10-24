import urllib.request
import json
import xml.etree.ElementTree as ET
import datetime

key = 'B80tS%2B2rS5Z3yFj6mNqYwE2JbUeQ%2BO2p7z2xO0P7YpGz%2F7v1xM2qXq8l9s4vH%2F6c9kL4bI5wZ3qR5yT%2BxV6g%3D%3D'
url = f'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev?serviceKey={key}&pageNo=1&numOfRows=1000&LAWD_CD=11440&DEAL_YMD=202407'

req = urllib.request.Request(url)
try:
    with urllib.request.urlopen(req) as response:
        xml_data = response.read()
        root = ET.fromstring(xml_data)
        for item in root.findall('.//item'):
            if item.findtext('지번') == '395' or '성산동' in item.findtext('법정동'):
                print(f"{item.findtext('아파트')} - {item.findtext('전용면적')} - {item.findtext('거래금액')}")
except Exception as e:
    print(e)
