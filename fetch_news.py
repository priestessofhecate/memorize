import json
import urllib.request
import xml.etree.ElementTree as ET
import re
from datetime import datetime

# 选用 Ars Technica 科技与开发前沿源（段落清晰、长度适中，支持直连）
RSS_URL = "https://feeds.arstechnica.com/arstechnica/technology-lab"

def clean_html(raw_html):
    """剔除 HTML 标签与多余空格/换行符"""
    clean_r = re.compile('<.*?>')
    text = re.sub(clean_r, '', raw_html)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_meaningful_paragraph(raw_desc, min_len=250, max_len=600):
    """提取 3~5 行（约 300~500 字符）结构完整的阅读文本"""
    clean_text = clean_html(raw_desc)
    
    # 如果抓到的文本过短，直接返回
    if len(clean_text) <= max_len:
        return clean_text
    
    # 在 300~550 字符之间寻找最近的一个句号，保证断句完整
    truncated = clean_text[:max_len]
    last_period = max(truncated.rfind('. '), truncated.rfind('? '), truncated.rfind('! '))
    
    if last_period > min_len:
        return truncated[:last_period + 1]
    return truncated + "..."

def fetch_rss():
    req = urllib.request.Request(
        RSS_URL, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    items = []

    # 抓取前 5 条精选
    for item in root.findall('./channel/item')[:5]:
        title = item.find('title').text if item.find('title') is not None else ""
        link = item.find('link').text if item.find('link') is not None else ""
        desc = item.find('description').text if item.find('description') is not None else ""
        
        detail_text = extract_meaningful_paragraph(desc)

        # 过滤掉内容过空的数据
        if len(detail_text) > 50:
            items.append({
                "title": title.strip(),
                "url": link.strip(),
                "summary": detail_text
            })

    news_data = {
        "updatedAt": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "articles": items
    }

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    print(f"✅ news.json 生成成功，已收录 {len(items)} 篇 3~5 行科技快讯")

if __name__ == '__main__':
    fetch_rss()
