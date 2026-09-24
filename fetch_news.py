import json
import urllib.request
import xml.etree.ElementTree as ET
import re

# 优质免翻墙/公共科技源 (示例：Hacker News 精选 或 GitHub 热门)
RSS_URL = "https://hnrss.org/frontpage"

def clean_html(raw_html):
    """去除 RSS 正文中的 HTML 标签，保留纯文本"""
    clean_r = re.compile('<.*?>')
    return re.sub(clean_r, '', raw_html).strip()

def fetch_rss():
    req = urllib.request.Request(RSS_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    items = []

    # 解析前 5 条短讯
    for item in root.findall('./channel/item')[:5]:
        title = item.find('title').text if item.find('title') is not None else ""
        link = item.find('link').text if item.find('link') is not None else ""
        desc = item.find('description').text if item.find('description') is not None else ""
        clean_desc = clean_html(desc)

        items.append({
            "title": title,
            "url": link,
            # 控制截取长度，适合英语初学者微阅读 (150字符左右)
            "summary": clean_desc[:200] + "..." if len(clean_desc) > 200 else clean_desc
        })

    news_data = {
        "updatedAt": re.sub(r'\..*', '', str(urllib.request.datetime.datetime.utcnow())),
        "articles": items
    }

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    print("✅ news.json 生成成功")

if __name__ == '__main__':
    fetch_rss()
