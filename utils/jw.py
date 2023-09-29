import requests
import re
import urllib.parse
import json
import os

raw_header = """
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Connection: keep-alive
"""

cas_login_raw_header = """
Host: passport.ustc.edu.cn
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: application/x-www-form-urlencoded
Content-Length: 190
Origin: https://passport.ustc.edu.cn
Connection: keep-alive
Referer: https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fjw.ustc.edu.cn%2Fucas-sso%2Flogin
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
"""

normal_headers = {i.split(": ")[0]: i.split(": ")[1] for i in raw_header.split("\n")[1:-1]}
cas_login_headers = {i.split(": ")[0]: i.split(": ")[1] for i in cas_login_raw_header.split("\n")[1:-1]}

USTC_PASSPORT_USERNAME = os.environ["USTC_PASSPORT_USERNAME"]
USTC_PASSPORT_PASSWORD = os.environ["USTC_PASSPORT_PASSWORD"]

def cas_login_data(lt: str) -> str:
    data = {
        "model":"uplogin.jsp",
        "CAS_LT":lt,
        "service":"https://jw.ustc.edu.cn/ucas-sso/login",
        "warn":"",
        "showCode":"",
        "qrcode": "",
        "username": USTC_PASSPORT_USERNAME,
        "password": USTC_PASSPORT_PASSWORD,
        "LT": "",
        "button": "",
    }
    cas_login_data = "&".join([f"{k}={urllib.parse.quote(v)}" for k, v in data.items()])
    return cas_login_data

def jw_login(s: requests.Session):
    url = "https://jw.ustc.edu.cn/"
    r = s.get(url, headers=normal_headers, allow_redirects=False)

    url = "https://jw.ustc.edu.cn/ucas-sso/login"
    r = s.get(url=url, headers=normal_headers, allow_redirects=False)

    url = "https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fjw.ustc.edu.cn%2Fucas-sso%2Flogin"
    r = s.get(url=url, headers=normal_headers, allow_redirects=False)
    token_pattern = re.compile(r"LT-[a-z0-9]+")
    lt = token_pattern.findall(r.text)[0]

    url = "https://passport.ustc.edu.cn/login"
    r = s.post(url=url, headers=cas_login_headers, data=cas_login_data(lt), allow_redirects=False)

    url = r.headers["Location"]
    r = s.get(url=url, headers=normal_headers, allow_redirects=False)

    url = r.headers["Location"]

def get_course_info(s: requests.Session, id_list: list[str]) -> json:
    """
    Notice: login first
    """
    url = "https://jw.ustc.edu.cn/ws/schedule-table/datum"
    data = {
        "lessonIds": id_list,
    }
    headers = normal_headers | {
        "Accept": "*/*",
        "Content-Type": "application/json;charset=UTF-8",
    }
    r = s.post(url=url, headers=headers, json=data, allow_redirects=False)
    return r.json()