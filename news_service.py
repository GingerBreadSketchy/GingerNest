import urllib.request
import json
import xml.etree.ElementTree as ET
import re
import time
from datetime import datetime
from html.parser import HTMLParser

_CACHE = {}
CACHE_EXPIRY_SECONDS = 300

def get_current_time():
    return time.time()

def make_request(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    with urllib.request.urlopen(req, timeout=10) as response:
        return response.read()

def parse_date(date_str):
    formats = [
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%Y-%m-%dT%H:%M:%S%z',
        '%a, %d %b %Y %H:%M:%S %Z',
        '%a, %d %b %Y %H:%M:%S %z',
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.isoformat() + 'Z'
        except ValueError:
            continue
    return date_str

def strip_html(text):
    text = re.sub('<[^<]+?>', '', text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&apos;', "'").replace('&#8217;', "'")
    text = text.replace('&#8211;', '-').replace('&#8216;', "'").replace('&#8230;', '...')
    text = text.replace('&#038;', '&').replace('&#x27;', "'").replace('&#x2F;', '/')
    return text.strip()

def extract_first_image(html_text):
    match = re.search(r'<img[^>]+src="([^"]+)"', html_text)
    if match:
        src = match.group(1)
        if src.startswith('//'):
            src = 'https:' + src
        return src
    return None

def fetch_space_articles():
    cache_key = "space_articles"
    now = get_current_time()
    if cache_key in _CACHE and (now - _CACHE[cache_key]["timestamp"]) < CACHE_EXPIRY_SECONDS:
        return _CACHE[cache_key]["data"]

    url = "https://api.spaceflightnewsapi.net/v4/articles/?limit=20"
    try:
        raw_data = make_request(url)
        data = json.loads(raw_data.decode('utf-8'))
        articles = []
        for item in data.get("results", []):
            articles.append({
                "id": f"space_art_{item.get('id')}",
                "title": item.get("title", "No Title"),
                "summary": item.get("summary", ""),
                "url": item.get("url", "#"),
                "image_url": item.get("image_url") or "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80",
                "news_site": item.get("news_site", "Spaceflight News"),
                "published_at": parse_date(item.get("published_at", "")),
                "category": "Spaceflight News",
                "authors": item.get("authors", [])
            })
        _CACHE[cache_key] = {"timestamp": now, "data": articles}
        return articles
    except Exception as e:
        print(f"Error fetching space articles: {e}")
        return _CACHE.get(cache_key, {}).get("data", [])

def fetch_space_blogs():
    cache_key = "space_blogs"
    now = get_current_time()
    if cache_key in _CACHE and (now - _CACHE[cache_key]["timestamp"]) < CACHE_EXPIRY_SECONDS:
        return _CACHE[cache_key]["data"]

    url = "https://api.spaceflightnewsapi.net/v4/blogs/?limit=20"
    try:
        raw_data = make_request(url)
        data = json.loads(raw_data.decode('utf-8'))
        blogs = []
        for item in data.get("results", []):
            blogs.append({
                "id": f"space_blog_{item.get('id')}",
                "title": item.get("title", "No Title"),
                "summary": item.get("summary", ""),
                "url": item.get("url", "#"),
                "image_url": item.get("image_url") or "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=600&q=80",
                "news_site": item.get("news_site", "Space Blog"),
                "published_at": parse_date(item.get("published_at", "")),
                "category": "Space Blogs",
                "authors": item.get("authors", [])
            })
        _CACHE[cache_key] = {"timestamp": now, "data": blogs}
        return blogs
    except Exception as e:
        print(f"Error fetching space blogs: {e}")
        return _CACHE.get(cache_key, {}).get("data", [])

def fetch_arxiv_ai():
    cache_key = "arxiv_ai"
    now = get_current_time()
    if cache_key in _CACHE and (now - _CACHE[cache_key]["timestamp"]) < CACHE_EXPIRY_SECONDS:
        return _CACHE[cache_key]["data"]

    url = "http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.LG&start=0&max_results=20&sortBy=submittedDate&sortOrder=descending"
    try:
        xml_data = make_request(url)
        root = ET.fromstring(xml_data)
        entries = root.findall('{http://www.w3.org/2005/Atom}entry')
        papers = []
        for i, entry in enumerate(entries):
            title_node = entry.find('{http://www.w3.org/2005/Atom}title')
            summary_node = entry.find('{http://www.w3.org/2005/Atom}summary')
            id_node = entry.find('{http://www.w3.org/2005/Atom}id')
            pub_node = entry.find('{http://www.w3.org/2005/Atom}published')

            title = title_node.text.strip().replace('\n', ' ') if title_node is not None else "No Title"
            title = re.sub(r'\s+', ' ', title)

            url_link = id_node.text.strip() if id_node is not None else "#"
            summary = summary_node.text.strip().replace('\n', ' ') if summary_node is not None else ""
            summary = re.sub(r'\s+', ' ', summary)
            pub_date = pub_node.text.strip() if pub_node is not None else ""

            authors = []
            author_nodes = entry.findall('{http://www.w3.org/2005/Atom}author')
            for auth in author_nodes:
                name_node = auth.find('{http://www.w3.org/2005/Atom}name')
                if name_node is not None:
                    authors.append({"name": name_node.text.strip(), "socials": None})

            papers.append({
                "id": f"arxiv_ai_{i}",
                "title": title,
                "summary": summary,
                "url": url_link,
                "image_url": "https://images.unsplash.com/photo-1677442136019-21780efad99a?auto=format&fit=crop&w=600&q=80",
                "news_site": "arXiv AI",
                "published_at": parse_date(pub_date),
                "category": "AI & Research",
                "authors": authors
            })
        _CACHE[cache_key] = {"timestamp": now, "data": papers}
        return papers
    except Exception as e:
        print(f"Error fetching arXiv papers: {e}")
        return _CACHE.get(cache_key, {}).get("data", [])

def fetch_rss_feed(url, category_name, default_source, fallback_img):
    cache_key = f"rss_{category_name.lower().replace(' ', '_')}_{default_source.lower()}"
    now = get_current_time()
    if cache_key in _CACHE and (now - _CACHE[cache_key]["timestamp"]) < CACHE_EXPIRY_SECONDS:
        return _CACHE[cache_key]["data"]

    try:
        xml_data = make_request(url)
        root = ET.fromstring(xml_data)

        # Support both RSS 2.0 (.//item) and Atom (.//entry) feeds
        items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')

        article_base_id = f"rss_{default_source.lower()}"

        articles = []
        for i, item in enumerate(items[:20]):
            # RSS title
            title_node = item.find('title')
            title = title_node.text.strip() if title_node is not None else "No Title"
            if hasattr(title_node, 'text') and not title:
                title = "No Title"
            title = re.sub(r'\s+', ' ', title)

            # RSS link
            link_node = item.find('link')
            if link_node is not None:
                link = link_node.text.strip() if link_node.text else link_node.get('href', '#')
            else:
                link = "#"

            # RSS description/summary
            desc_node = item.find('description')
            summary_text = ""
            if desc_node is not None and desc_node.text:
                summary_text = desc_node.text.strip()

            # For Atom feeds, use summary or content
            if not summary_text:
                summary_node = item.find('{http://www.w3.org/2005/Atom}summary')
                if summary_node is None:
                    summary_node = item.find('{http://www.w3.org/2005/Atom}content')
                if summary_node is not None and summary_node.text:
                    summary_text = summary_node.text.strip()

            if summary_text:
                summary = strip_html(summary_text)
                # Hacker News RSS sends "Comments" as every description — replace with title
                if summary.lower().strip() in ('comments', 'no summary available.', ''):
                    summary = title
                # Truncate absurdly long summaries
                if len(summary) > 600:
                    summary = summary[:597] + '...'
            else:
                summary = title

            # RSS pubDate
            pub_node = item.find('pubDate')
            if pub_node is None:
                pub_node = item.find('{http://www.w3.org/2005/Atom}published')
            if pub_node is None:
                pub_node = item.find('{http://www.w3.org/2005/Atom}updated')
            pub_date = pub_node.text.strip() if pub_node is not None else ""

            # Thumbnail extraction: multiple strategies
            image_url = None
            best_width = 0

            # 1. Check media:thumbnail / media:content namespaced elements
            #    Tags like {http://search.yahoo.com/mrss/}thumbnail have "thumbnail" in tag
            for child in item:
                tag_lower = child.tag.lower()
                has_thumbnail = 'thumbnail' in tag_lower
                has_content = 'content' in tag_lower and 'encoded' not in tag_lower
                if has_thumbnail or has_content:
                    url = child.attrib.get('url') or child.attrib.get('src')
                    if url:
                        width = int(child.attrib.get('width', 0))
                        if width >= best_width:
                            image_url = url
                            best_width = width

            # 2. Check enclosure tag
            if not image_url:
                enclosure = item.find('enclosure')
                if enclosure is not None:
                    enc_type = enclosure.attrib.get('type', '')
                    if 'image' in enc_type:
                        image_url = enclosure.attrib.get('url')

            # 3. Parse description HTML for the first <img> tag
            if not image_url and desc_node is not None and desc_node.text:
                image_url = extract_first_image(desc_node.text)

            # 4. Check content:encoded (NASA, etc.) for images
            if not image_url:
                for child in item:
                    if 'encoded' in child.tag.lower():
                        if child.text:
                            image_url = extract_first_image(child.text)
                            if image_url:
                                break

            # 5. For Atom feeds, check content for images
            if not image_url:
                content_node = item.find('{http://www.w3.org/2005/Atom}content')
                if content_node is not None and content_node.text:
                    image_url = extract_first_image(content_node.text)

            # 6. For Atom feeds, check link rel="enclosure"
            if not image_url:
                for link_el in item.findall('{http://www.w3.org/2005/Atom}link'):
                    if link_el.attrib.get('rel') == 'enclosure' or link_el.attrib.get('type', '').startswith('image'):
                        image_url = link_el.attrib.get('href')
                        if image_url:
                            break

            if not image_url:
                image_url = fallback_img

            if image_url == fallback_img and 'unsplash' in fallback_img:
                src_lower = default_source.lower()
                if 'africa' in src_lower or 'guardian' in src_lower:
                    pool = [
                        "https://images.unsplash.com/photo-1523805009345-7448845a9e53?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1580651315530-69c8e0026377?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1574484284002-952d92456975?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1523805009345-7448845a9e53?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1626200419199-391ae4be7a41?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1612878010854-1250dfc791c6?auto=format&fit=crop&w=600&q=80",
                    ]
                elif 'science' in src_lower or 'daily' in src_lower:
                    pool = [
                        "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1564325724739-bae0bd08762c?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1507413245164-6160d8298b31?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1554475901-4538ddfbccc2?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1507413245164-6160d8298b31?auto=format&fit=crop&w=600&q=80",
                    ]
                elif 'cnbc' in src_lower or 'bloomberg' in src_lower or 'yahoo' in src_lower:
                    pool = [
                        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=600&q=80",
                    ]
                elif 'coindesk' in src_lower or 'cointelegraph' in src_lower or 'decrypt' in src_lower:
                    pool = [
                        "https://images.unsplash.com/photo-1621761191319-c6fb62004040?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1555072956-7758afb20e8f?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1631603090989-93f9ef62f4d4?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1642790551116-18e150f248e5?auto=format&fit=crop&w=600&q=80",
                    ]
                elif 'investing' in src_lower:
                    pool = [
                        "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1616077168070-5cb5f5f0a3e0?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1580519542036-c47de6196ba5?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1569025690938-a00729c9e1f9?auto=format&fit=crop&w=600&q=80",
                    ]
                elif 'business' in src_lower or 'bbc' in src_lower:
                    pool = [
                        "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=600&q=80",
                    ]
                else:
                    pool = [
                        "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1499750310107-5fef28a66643?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1531297484001-80022131f5a1?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=600&q=80",
                        "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=600&q=80",
                    ]
                idx = i % len(pool)
                image_url = pool[idx]

            article_id = f"{article_base_id}_{i}"

            articles.append({
                "id": article_id,
                "title": title,
                "summary": summary,
                "url": link,
                "image_url": image_url,
                "news_site": default_source,
                "published_at": parse_date(pub_date),
                "category": category_name,
                "authors": [{"name": default_source, "socials": None}]
            })

        _CACHE[cache_key] = {"timestamp": now, "data": articles}
        return articles
    except Exception as e:
        print(f"Error fetching RSS feed {url}: {e}")
        return _CACHE.get(cache_key, {}).get("data", [])

def fetch_reddit_tech():
    url = "https://www.reddit.com/r/technology/hot/.rss"
    return fetch_rss_feed(
        url=url,
        category_name="Technology",
        default_source="Reddit Technology",
        fallback_img="https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=600&q=80"
    )

def fetch_all_news(force_refresh=False):
    if force_refresh:
        _CACHE.clear()

    # Category 1: Spaceflight News
    space_art = fetch_space_articles()
    nasa_feed = fetch_rss_feed(
        url="https://www.nasa.gov/feed/",
        category_name="Spaceflight News",
        default_source="NASA News",
        fallback_img="https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80"
    )
    space_combined = space_art + nasa_feed

    # Category 2: Space Blogs
    space_blogs = fetch_space_blogs()

    # Category 3: Technology
    techcrunch = fetch_rss_feed(
        url="https://techcrunch.com/feed/",
        category_name="Technology",
        default_source="TechCrunch",
        fallback_img="https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?auto=format&fit=crop&w=600&q=80"
    )
    hacker_news = fetch_rss_feed(
        url="https://news.ycombinator.com/rss",
        category_name="Technology",
        default_source="Hacker News",
        fallback_img="https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=600&q=80"
    )
    the_verge = fetch_rss_feed(
        url="https://www.theverge.com/rss/index.xml",
        category_name="Technology",
        default_source="The Verge",
        fallback_img="https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=600&q=80"
    )
    wired = fetch_rss_feed(
        url="https://www.wired.com/feed/rss",
        category_name="Technology",
        default_source="Wired",
        fallback_img="https://images.unsplash.com/photo-1504639725590-34d0984388bd?auto=format&fit=crop&w=600&q=80"
    )
    reddit_tech = fetch_reddit_tech()
    tech_combined = techcrunch + hacker_news + the_verge + wired + reddit_tech

    # Category 4: AI & Research
    arxiv_ai = fetch_arxiv_ai()

    # Category 5: Science
    sciencedaily = fetch_rss_feed(
        url="https://www.sciencedaily.com/rss/all.xml",
        category_name="Science",
        default_source="ScienceDaily",
        fallback_img="https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=600&q=80"
    )

    # Category 6: Business
    bbc_business = fetch_rss_feed(
        url="https://feeds.bbci.co.uk/news/business/rss.xml",
        category_name="Business",
        default_source="BBC Business",
        fallback_img="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=600&q=80"
    )
    cnbc = fetch_rss_feed(
        url="https://www.cnbc.com/id/100003114/device/rss/rss.html",
        category_name="Business",
        default_source="CNBC",
        fallback_img="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=600&q=80"
    )
    bloomberg = fetch_rss_feed(
        url="https://feeds.bloomberg.com/markets/news.rss",
        category_name="Business",
        default_source="Bloomberg",
        fallback_img="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=600&q=80"
    )
    yahoo_finance = fetch_rss_feed(
        url="https://finance.yahoo.com/news/rssindex",
        category_name="Business",
        default_source="Yahoo Finance",
        fallback_img="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=600&q=80"
    )
    business_combined = bbc_business + cnbc + bloomberg + yahoo_finance

    # Category 7: Crypto
    coindesk = fetch_rss_feed(
        url="https://www.coindesk.com/arc/outboundfeeds/rss/",
        category_name="Crypto",
        default_source="CoinDesk",
        fallback_img="https://images.unsplash.com/photo-1621761191319-c6fb62004040?auto=format&fit=crop&w=600&q=80"
    )
    cointelegraph = fetch_rss_feed(
        url="https://cointelegraph.com/rss",
        category_name="Crypto",
        default_source="CoinTelegraph",
        fallback_img="https://images.unsplash.com/photo-1639762681485-074b7f938ba0?auto=format&fit=crop&w=600&q=80"
    )
    decrypt = fetch_rss_feed(
        url="https://decrypt.co/feed",
        category_name="Crypto",
        default_source="Decrypt",
        fallback_img="https://images.unsplash.com/photo-1639762681485-074b7f938ba0?auto=format&fit=crop&w=600&q=80"
    )
    crypto_combined = coindesk + cointelegraph + decrypt

    # Category 8: Forex
    investing = fetch_rss_feed(
        url="https://www.investing.com/rss/news.rss",
        category_name="Forex",
        default_source="Investing.com",
        fallback_img="https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=600&q=80"
    )

    # Category 9: Africa News
    bbc_africa = fetch_rss_feed(
        url="https://feeds.bbci.co.uk/news/world/africa/rss.xml",
        category_name="Africa",
        default_source="BBC Africa",
        fallback_img="https://images.unsplash.com/photo-1523805009345-7448845a9e53?auto=format&fit=crop&w=600&q=80"
    )
    guardian_africa = fetch_rss_feed(
        url="https://www.theguardian.com/world/africa/rss",
        category_name="Africa",
        default_source="The Guardian Africa",
        fallback_img="https://images.unsplash.com/photo-1580651315530-69c8e0026377?auto=format&fit=crop&w=600&q=80"
    )
    africa_combined = bbc_africa + guardian_africa

    # Category 10: World News
    bbc_world = fetch_rss_feed(
        url="http://feeds.bbci.co.uk/news/world/rss.xml",
        category_name="World News",
        default_source="BBC News",
        fallback_img="https://images.unsplash.com/photo-1504711434969-e33886168d8c?auto=format&fit=crop&w=600&q=80"
    )
    the_guardian = fetch_rss_feed(
        url="https://www.theguardian.com/world/rss",
        category_name="World News",
        default_source="The Guardian",
        fallback_img="https://images.unsplash.com/photo-1588681663908-4c82b9e8a94b?auto=format&fit=crop&w=600&q=80"
    )
    npr = fetch_rss_feed(
        url="https://feeds.npr.org/1004/rss.xml",
        category_name="World News",
        default_source="NPR",
        fallback_img="https://images.unsplash.com/photo-1495020689067-958852a7765e?auto=format&fit=crop&w=600&q=80"
    )
    world_combined = bbc_world + the_guardian + npr

    return {
        "space_articles": space_combined,
        "space_blogs": space_blogs,
        "tech_news": tech_combined,
        "science": sciencedaily,
        "ai_research": arxiv_ai,
        "business": business_combined,
        "crypto": crypto_combined,
        "forex": investing,
        "africa": africa_combined,
        "world_news": world_combined,
        "all": space_combined + space_blogs + tech_combined + sciencedaily + arxiv_ai + business_combined + crypto_combined + investing + africa_combined + world_combined
    }