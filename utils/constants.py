from utils.tools import parse_header

_normal_header = """
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Connection: keep-alive
"""

_cas_login_raw_header = """
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8
Accept-Encoding: gzip, deflate, br, zstd
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Cache-Control: no-cache
Connection: keep-alive
Content-Length: 221
Content-Type: application/x-www-form-urlencoded
DNT: 1
Host: passport.ustc.edu.cn
Origin: https://passport.ustc.edu.cn
Pragma: no-cache
Priority: u=0, i
Referer: https://passport.ustc.edu.cn/login
sec-ch-ua: "Edge";v="114", "Chromium";v="114", "Not=A?Brand";v="24"
sec-ch-ua-mobile: ?0: ec-ch-ua-platform: "Windows"
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
Sec-GPC: 1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0
"""

_catalog_raw_header = """
Host: catalog.ustc.edu.cn
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0
Accept: application/json, text/plain, */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
Referer: http://catalog.ustc.edu.cn/query/lesson
"""

normal_headers = parse_header(_normal_header)
cas_login_headers = parse_header(_cas_login_raw_header)
catalog_headers = parse_header(_catalog_raw_header)
