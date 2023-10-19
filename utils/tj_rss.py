"""
Make RSS feed from: http://www.tj.ustc.edu.cn/tzgg/list.htm

Save rss to outputDir/tj_ustc.xml
"""
import datetime
import os

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from requests.adapters import HTTPAdapter

url = "http://www.tj.ustc.edu.cn/tzgg/list.htm"
title = "体育教学中心"
description = "体育教学中心，http://www.tj.ustc.edu.cn"

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57"
}

"""
HTML looks like this:
```html
<body>
<div class="section page-xstzcs">
<div class="container clearfix">
<div class="content pull-right">
<div class="content-body">
<div frag="面板5">
<div frag="窗口5" portletmode="simpleList" >
<div id="wp_news_w5">
<ul>
    <li class="item">
        <a href="/2023/0614/c30734a605933/page.htm"><a href='/2023/0614/c30734a605933/page.htm' target='_blank' title='我校羽毛球队包揽首届安徽省高校羽毛球交流赛冠亚军'>我校羽毛球队包揽首届安徽省高校羽毛球交流赛冠亚军</a></a>
        <time>2023-06-14</time>
    </li>
    <li class="item">
        <a href="/2023/0613/c30734a605794/page.htm"><a href='/2023/0613/c30734a605794/page.htm' target='_blank' title='体育教学中心教师参加第五届中国体育非物质文化遗产大会并作专题报告'>体育教学中心教师参加第五届中国体育非物质文化遗产大会并作专题...</a></a>
        <time>2023-06-13</time>
    </li>
```
(Unnecessary parts are omitted)

First we need to parse a given html string like this one to a list like this:
```python
[
    {
        "title": "我校羽毛球队包揽首届安徽省高校羽毛球交流赛冠亚军",
        "link": "http://www.tj.ustc.edu.cn/2023/0614/c30734a605933/page.htm",
        "date": <datetime.datetime object>
    },
    {
        "title": "体育教学中心教师参加第五届中国体育非物质文化遗产大会并作专题报告",
        "link": "http://www.tj.ustc.edu.cn/2023/0613/c30734a605794/page.htm",
        "date": <datetime.datetime object>
    },
    ...
]
"""


def parseHTML(html: str):
    """
    Parse a given html string to a list of dicts

    :param str html: The html string to parse

    :return: A list of dicts
    :rtype: list
    :raises: None
    """
    soup = BeautifulSoup(html, "html.parser")
    ul = soup.find("div", {"id": "wp_news_w5"}).find("ul")
    items = ul.find_all("li", {"class": "item"})
    result = []
    for item in items:
        date_raw = item.find("time").text

        date = datetime.datetime.strptime(
            date_raw, "%Y-%m-%d"
        ).astimezone(
            tz=datetime.timezone(datetime.timedelta(hours=8))
        )

        result.append({
            "title": item.find("a").text,
            # 'http://www.tj.ustc.edu.cn' + '/2023/0614/c30734a605933/page.htm
            "link": 'http://www.tj.ustc.edu.cn' + item.find("a")['href'],
            "date": date
        })
    return result


def tj_ustc_RSS(output_dir: str):
    """
    Make RSS feed from: http://www.tj.ustc.edu.cn/tzgg/list.htm, save rss to outputDir/xml/tj_ustc.xml

    :param str output_dir: The directory to save the generated RSS feed
    """

    s = requests.Session()
    s.mount("http://", HTTPAdapter(max_retries=3))
    r = s.get(url, headers=headers)
    r.encoding = "utf-8"
    html = r.text

    items = parseHTML(html)

    fg = FeedGenerator()
    fg.title(title)
    fg.description(description)
    fg.link(href="http://www.tj.ustc.edu.cn/tzgg/list.htm", rel="alternate")
    fg.language("zh-CN")
    fg.lastBuildDate(datetime.datetime.utcnow().astimezone(tz=datetime.timezone.utc))
    fg.ttl(5)

    for item in items:
        fe = fg.add_entry()
        fe.title(item["title"])
        fe.link(href=item["link"])
        fe.pubDate(item["date"])

    fg.rss_file(os.path.join(output_dir, "tj_ustc.xml"))
