
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from html import unescape

FEEDS = {
    "Technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "Science": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "Business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "World": "https://feeds.bbci.co.uk/news/world/rss.xml"
}

def clean_text(value):
    value = re.sub(r"<[^>]+>", "", value or "")
    return unescape(value).strip()

articles = []
seen = set()

for category, feed_url in FEEDS.items():
    try:
        request = urllib.request.Request(
            feed_url,
            headers={"User-Agent": "NexoraNewsBot/1.0"}
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            root = ET.fromstring(response.read())

        for item in root.findall(".//item"):
            title = clean_text(item.findtext("title"))
            link = (item.findtext("link") or "").strip()
            summary = clean_text(item.findtext("description"))

            if not title or not link or link in seen:
                continue

            seen.add(link)
            articles.append({
                "title": title,
                "summary": summary[:400],
                "category": category,
                "url": link
            })

    except Exception as error:
        print(f"Could not fetch {category}: {error}")

output = Path("data/news.json")
output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w", encoding="utf-8") as file:
    json.dump(articles, file, ensure_ascii=False, indent=2)

print(f"Saved {len(articles)} news articles.")
