import urllib.request
import xml.etree.ElementTree as ET
import json
import re
import html
from datetime import datetime

# 精选外媒科技 RSS 源
RSS_FEEDS = [
    "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "https://www.theverge.com/rss/index.xml",
    "https://techcrunch.com/feed/"
]

def clean_html(raw_html):
    if not raw_html:
        return ""
    # 去除 HTML 标签、多余转义符及媒体特有占位符
    text = re.sub(r'<[^>]+>', '', raw_html)
    text = html.unescape(text)
    text = re.sub(r'Enlarge\s*/\s*', '', text)
    text = re.sub(r'\[\s*Read more\s*\.\.\.\s*\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def split_into_sentences(text):
    # 按标准英文标点断句，保留完整句子
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"\'])', text)
    clean_sents = [s.strip() for s in sentences if len(s.strip()) > 15 and not s.strip().startswith("Photo:")]
    return clean_sents

def extract_news():
    articles = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) MemorizeNewsBot/2.0'}

    for feed_url in RSS_FEEDS:
        try:
            req = urllib.request.Request(feed_url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as response:
                xml_data = response.read()
            
            root = ET.fromstring(xml_data)
            
            # 支持 RSS 2.0 与 Atom 格式
            items = root.findall('.//item')
            if not items:
                items = root.findall('.//{http://www.w3.org/2005/Atom}entry')

            for item in items[:4]:
                # 1. 原汁原味标题
                title_elem = item.find('title') if item.find('title') is not None else item.find('{http://www.w3.org/2005/Atom}title')
                title = clean_html(title_elem.text if title_elem is not None else "Tech Brief")

                # 2. 链接
                link = ""
                link_elem = item.find('link') if item.find('link') is not None else item.find('{http://www.w3.org/2005/Atom}link')
                if link_elem is not None:
                    link = link_elem.text or link_elem.attrib.get('href', '')

                # 3. 正文提炼与完整段落拆解
                desc_elem = item.find('description') or item.find('{http://www.w3.org/2005/Atom}content') or item.find('{http://www.w3.org/2005/Atom}summary')
                raw_desc = desc_elem.text if desc_elem is not None else ""
                clean_body = clean_html(raw_desc)

                if len(clean_body) < 60:
                    continue

                all_sentences = split_into_sentences(clean_body)
                if not all_sentences:
                    continue

                # 外层提取 1~2 句完整核心导语（TL;DR）
                essence = " ".join(all_sentences[:2])
                
                # 内层保留 3~5 句完整资讯段落
                full_body_sents = all_sentences[:6]
                full_body = " ".join(full_body_sents)

                articles.append({
                    "id": f"art_{len(articles) + 1}",
                    "title": title,
                    "essence": essence,
                    "full_body": full_body,
                    "sentences": full_body_sents,
                    "url": link
                })

                if len(articles) >= 6:
                    break
        except Exception as e:
            print(f"Fetch feed error ({feed_url}): {e}")

        if len(articles) >= 6:
            break

    # 输出规范化的 news.json
    output_data = {
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "articles": articles
    }

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"Successfully generated news.json with {len(articles)} articles.")

if __name__ == "__main__":
    extract_news()
