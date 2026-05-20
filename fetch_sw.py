import urllib.request

try:
    url = "https://xn--2z2b21z2vav20a.kr/sw.js"
    req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(req) as res:
        content = res.read().decode('utf-8')
        print(content[:100])
except Exception as e:
    print(e)
