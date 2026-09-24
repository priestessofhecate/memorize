import json
import urllib.request
import xml.etree.ElementTree as ET
import re
from datetime import datetime

RSS_URL = "https://hnrss.org/frontpage"

def clean_html(raw_html):
    clean_r = re.compile('<.*?>')
    return re.sub(clean_r, '', raw_html).strip()

def fetch_rss():
    req = urllib.request.Request(RSS_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    items = []

    for item in root.findall('./channel/item')[:5]:
        title = item.find('title').text if item.find('title') is not None else ""
        link = item.find('link').text if item.find('link') is not None else ""
        desc = item.find('description').text if item.find('description') is not None else ""
        clean_desc = clean_html(desc)

        items.append({
            "title": title,
            "url": link,
            "summary": clean_desc[:200] + "..." if len(clean_desc) > 200 else clean_desc
        })

    news_data = {
        "updatedAt": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "articles": items
    }

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    print("✅ news.json 生成成功")

if __name__ == '__main__':
    fetch_rss()
