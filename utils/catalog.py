import requests
import json

raw_header = """
Host: catalog.ustc.edu.cn
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0
Accept: application/json, text/plain, */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
Referer: http://catalog.ustc.edu.cn/query/lesson
"""
headers = {i.split(": ")[0]: i.split(": ")[1] for i in raw_header.split("\n")[1:-1]}

def get_token() -> str:
    url = "https://catalog.ustc.edu.cn/get_token"
    r = requests.get(url=url, headers=headers, allow_redirects=False)
    return r.json()["access_token"]

def get_semester_list() -> json:
    url = "https://catalog.ustc.edu.cn/api/teach/semester/list?access_token=" + get_token()
    r = requests.get(url=url, headers=headers, allow_redirects=False)
    return r.json()

def get_course_list(id: str) -> json:
    url = "https://catalog.ustc.edu.cn/api/teach/lesson/list-for-teach/" + id + "?access_token=" + get_token()
    r = requests.get(url=url, headers=headers, allow_redirects=False)
    return r.json()