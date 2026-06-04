# GingerNest: Consolidated News Dashboard

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![GitHub Profile](https://img.shields.io/badge/GitHub-GingerBreadSketchy-181717?style=for-the-badge&logo=github)](https://github.com/GingerBreadSketchy)

GingerNest aggregates and normalizes news from 27+ sources across 10 categories into a sleek, professional web dashboard with persistent bookmarks, real-time search, and full dark/light mode.

---

## Key Features

### Data Layer (`news_service.py`)
- **27+ Sources / 10 Categories**: Spaceflight News, Space Blogs, Technology (The Verge, Wired, TechCrunch, HN, Reddit), Science, AI & Research, Business (CNBC, Bloomberg, Yahoo Finance, BBC), Crypto (CoinDesk, CoinTelegraph, Decrypt), Forex (Investing.com), Africa (BBC Africa, Guardian Africa), World News (BBC, Guardian, NPR)
- **Zero external dependencies**: Built on stdlib (`urllib`, `xml.etree.ElementTree`). No `feedparser`, `requests`, or `beautifulsoup`.
- **5-minute in-memory cache**: Prevents API rate-limiting across refreshes.
- **Smart thumbnail extraction**: Extracts real images from `media:content`, `media:thumbnail`, `<enclosure>`, `<img>` in descriptions, and `content:encoded`. Falls back to category-themed Unsplash pools when feeds lack images (TechCrunch, HN, ScienceDaily, NPR, arXiv).
- **Uniform schema**: `id`, `title`, `summary`, `url`, `image_url`, `news_site`, `published_at`, `category`, `authors`.

### Web Dashboard (`app.py` + `templates/index.html`)
- **Persistent bookmarks** via local `favorites.json` — survives server restarts
- **10 filter tabs**: All, Space, Space Blogs, Technology, Science, AI & Research, Business, Crypto, Forex, Africa, World News, Bookmarks
- **Live search** across headlines, summaries, and publishers
- **Publisher dropdown** dynamically computed from loaded sources
- **Sort options**: Newest, Oldest, Alphabetical
- **Grid / List view** toggle with staggered card entrance animations
- **Detail modal** with bookmark, copy-link, and read-publisher actions
- **Light/Dark mode** persisted to localStorage
- **Shimmer skeleton loaders**, toast notifications, scroll-to-top button
- **Responsive**: 1-col mobile → 4-col xl, horizontally scrollable category tabs, full-width modals on mobile

---

## Deployment on PythonAnywhere

### 1. Upload the project
Clone or upload the `news webapp py` folder to your PythonAnywhere account. Via Bash console:
```bash
git clone <your-repo-url>
```
Or use the Files tab to upload the zip.

### 2. Create a web app
- Go to the **Web** tab → **Add a new web app**
- Choose **Manual configuration** → **Python 3.10+**
- Set **Source code**: `/home/<username>/news webapp py`
- Set **Working directory**: `/home/<username>/news webapp py`
- Set **WSGI configuration file**: `/var/www/<username>_pythonanywhere_com_wsgi.py`

### 3. Edit the WSGI file
Replace the WSGI file content with:
```python
import sys
sys.path.insert(0, '/home/<username>/news webapp py')

from app import app as application
```

### 4. Install Flask
Open a **Bash console** and run:
```bash
pip install flask
```

### 5. Reload
Click the **Reload** button on the Web tab. Your app will be live at `https://<username>.pythonanywhere.com`.

> **Note**: `favorites.json` persists across reloads on PythonAnywhere. RSS fetch timeout is 10s by default — if feeds time out, consider reducing `CACHE_EXPIRY_SECONDS` in `news_service.py` or using the **Always-on** paid plan.

---

## Local Development

### Setup
```bash
pip install flask
```

### Run
```bash
python app.py
```
Open **http://localhost:5000** in your browser.

### API Endpoints
| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serves the dashboard |
| `/api/news` | GET | Returns all articles as JSON. Add `?force_refresh=true` to bypass cache |
| `/api/favorites` | GET | List all bookmarked articles |
| `/api/favorites` | POST | Add an article to bookmarks |
| `/api/favorites/<id>` | DELETE | Remove a bookmark |
| `/api/sources` | GET | List all unique publisher names |

---

## Project Structure
```
├── app.py               # Flask server & favorites API
├── news_service.py      # Feed aggregation, caching, thumbnail extraction
├── templates/
│   └── index.html       # Full SPA frontend (Tailwind CSS + vanilla JS)
├── favorites.json       # Auto-generated bookmarks database
└── README.md
```

---

## Sources
- **Spaceflight News API** • **NASA** • **ESA** • **SpaceNews** • **NASASpaceflight**
- **TechCrunch** • **Hacker News** • **The Verge** • **Wired** • **Reddit Technology**
- **arXiv AI**
- **ScienceDaily**
- **BBC Business** • **CNBC** • **Bloomberg** • **Yahoo Finance**
- **CoinDesk** • **CoinTelegraph** • **Decrypt**
- **Investing.com**
- **BBC Africa** • **The Guardian Africa**
- **BBC News** • **The Guardian** • **NPR**