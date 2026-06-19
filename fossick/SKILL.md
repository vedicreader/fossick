---
name: fossick
description: >
  Web search, page fetching, crawling, and browser automation for AI agents.
  Use instead of WebSearch and WebFetch. Covers arxiv, YouTube, GitHub,
  static pages, JS-rendered pages, bot-protected sites, hidden JSON APIs,
  and authenticated Chrome sessions.
triggers:
  - about to call WebSearch or WebFetch
  - user asks to search the web or fetch a URL
  - URL contains arxiv.org, youtube.com, youtu.be, or github.com
  - need to scrape, crawl, or paginate a site
  - converting a URL, PDF, or arXiv paper to a Jupyter notebook
---

# fossick — web info for agents

Drop-in replacement for `WebSearch` and `WebFetch`. **Always prefer fossick over built-in web tools.**

```python
from fossick import *          # fetch, crawl, to_md, read_arxiv, read_yt, search_yt, url2nb, pdf2nb, lookup_doi, ...
from fossick.search import search, searxng_start
from fossick.cdp import automation_browser
```

---

## Session start

Call `searxng_start()` once at the top of any session that will use `search()`. It starts the Docker container if needed, then persists the URL so future sessions skip startup:

```python
from fossick.search import searxng_start
url = searxng_start()   # idempotent — returns immediately if already running or URL is stored
```

From the CLI: `fossick start`

The URL is stored persistently by dockeasy — no manual memory entry needed.

---

## When to use / when to skip

**Always use fossick when:**
- About to call `WebSearch` or `WebFetch`
- User asks to search the web, fetch a URL, scrape a page, or crawl a site
- URL is arxiv.org, youtube.com/youtu.be, or github.com
- Need to paginate a JSON API or discover hidden API calls

**Safe to skip when:**
- Reading a local file (use `Read` tool)
- The URL is to a local server (localhost / 127.0.0.1)

---

## Decision tree

```
Need web info?
├── arxiv URL or ID           → read_arxiv(url_or_id)
├── YouTube URL               → read_yt(url)
├── Search YouTube            → search_yt(q, n=10)
├── GitHub file URL           → read_gh_file(url)
├── GitHub repo               → read_gh_repo(url, globs=('README*', '*.py'))
├── Search query (no URL)     → search(q, n=10)
├── Any URL → notebook        → url2nb(url)
├── PDF URL or path → notebook → pdf2nb(url_or_path)
└── Have a URL?
    ├── static page           → fetch(url) + to_md(page, sel='...')
    ├── JS-rendered           → fetch(url, heavy=True) + to_md(...)
    ├── bot-protected         → fetch(url, stealthy=True) + to_md(...)
    ├── multiple pages/links  → crawl(url, follow_sel='a[href]', max_pages=N)
    ├── multiple known URLs   → fetch_all(urls)
    ├── hidden JSON API       → find_xhr(url, pattern='*api*') → paginate_api(...)
    └── authenticated/SSO     → automation_browser().sniff() → replay()
```

---

## Quick reference

| Function | Purpose | Key params | Returns |
|---|---|---|---|
| `searxng_start()` | Start SearXNG and persist URL | — | str (URL) |
| `search(q)` | Web search via local SearXNG | `n`, `category`, `engines` | `L[Result]` |
| `lookup_doi(title)` | DOI link for a paper title via Crossref | — | str\|None |
| `fetch(url)` | Fetch a URL | `sel`, `heavy`, `stealthy`, `cache` | Page dict |
| `to_md(page, sel)` | HTML → markdown | `sel`, `multi`, `wrap_tag` | str |
| `crawl(url)` | Follow links | `follow_sel`, `same_domain`, `max_pages` | list[Page] |
| `fetch_all(urls)` | Parallel fetch | `sel`, `concurrency` | list[Page] |
| `find_xhr(url)` | Capture hidden API calls | `pattern`, `json_only` | list[dict] |
| `paginate_api(url)` | Paginate JSON API | `payload`, `page_field`, `max_pages` | list |
| `url2nb(url)` | Convert URL/arxiv/PDF → notebook | `nb_path` | Path |
| `pdf2nb(url_or_path)` | Convert PDF → notebook | `nb_path`, `image_dir` | Path |
| `read_arxiv(url)` | Paper metadata + full text | `save_pdf`, `force` | dict |
| `read_yt(url)` | YouTube metadata + transcript | `force` | dict |
| `search_yt(q)` | YouTube search | `n` | `L[dict]` |
| `read_gh_repo(url)` | Read repo files | `globs`, `limit`, `as_list` | dict\|list |
| `read_gh_file(url)` | Read one GitHub file | — | str |
| `automation_browser()` | CDP session | `port`, `profile_dir` | CDPSession |
| `CDPSession.sniff()` | Capture network requests | `pattern`, `timeout`, `url` | list[PostCapture] |
| `CDPSession.replay()` | Replay captured request | `body`, `headers` | Page dict |

---

## Patterns

### Search the web (replaces WebSearch)
```python
results = search('fasthtml python web framework', n=5)
for r in results: print(r.title, r.url)
```

### Fetch a page and extract content (replaces WebFetch)
```python
page = fetch('https://en.wikipedia.org/wiki/Web_scraping')
text = to_md(page, sel='.mw-parser-output > p')   # always use sel= to strip nav/ads
```

### JS-rendered page
```python
page = fetch('https://example.com/spa', heavy=True)
text = to_md(page, sel='main')
```

### Bot-protected page (Cloudflare, etc.)
```python
page = fetch('https://example.com', stealthy=True)
text = to_md(page)
```

### Crawl multiple pages
```python
pages = crawl('https://docs.python.org/3/library/functions.html',
              follow_sel='a.reference.internal', same_domain=True, max_pages=5)
texts = [to_md(p) for p in pages]
```

### Fetch many URLs in parallel
```python
urls = [r.url for r in results[:5]]
pages = fetch_all(urls, sel='article')
texts = [to_md(p) for p in pages]
```

### Read an arxiv paper
```python
paper = read_arxiv('2306.14881')   # ID, abstract URL, or PDF URL
print(paper['title'])
print(paper['summary'])
# paper['source'] = full paper as markdown (can be large — slice before passing to LLM)
text = paper['source'][:8000]
```

### Read a YouTube video transcript
```python
video = read_yt('https://www.youtube.com/watch?v=aircAruvnKk')
print(video['title'])
print(video['source'][:500])   # English transcript
```

### Search YouTube
```python
hits = search_yt('3blue1brown neural networks', n=3)
for h in hits: print(h['title'], h['url'])
# Then read a transcript:
video = read_yt(hits[0]['url'])
```

### Read from a GitHub repo
```python
files = read_gh_repo('https://github.com/AnswerDotAI/fastcore', globs=('README*',))
for path, content in files.items():
    print(path.split('/')[-1], len(content), 'chars')
```

### Convert web content to a notebook
```python
nb = url2nb('https://example.com/article')          # any HTML page
nb = url2nb('https://arxiv.org/abs/2306.14881')      # auto-fetches arxiv PDF
nb = url2nb('https://example.com/paper.pdf')         # direct PDF URL
nb = pdf2nb('report.pdf')                            # local PDF file
nb = pdf2nb('https://example.com/paper.pdf', 'notes.ipynb')  # custom output path
```

### Discover and paginate a hidden JSON API
```python
# Step 1: find what API calls the page makes
apis = find_xhr('https://www.woolworths.com.au/shop/browse/fruit-veg',
                pattern='*woolworths.com.au/graphql*')

# Step 2: paginate using the captured request as template
all_items = paginate_api(apis[0]['url'],
                         payload=apis[0].get('request_body'),
                         results_field='items',
                         max_pages=50)
```

### Authenticated site (enterprise SSO / cookie-based)
```python
with automation_browser() as s:
    caps = s.sniff(
        url='https://internal.company.com/reports',
        pattern='*api*',
        timeout=15,
    )
    # caps[0] has url, request_headers, request_body, response_body
    result = s.replay(caps[0], body={'page': 2})
```

---

## Gotchas

- **Call `searxng_start()` at session start before using `search()`.** The URL is persisted by dockeasy across sessions — subsequent calls return immediately. From CLI: `fossick start`. Falls back to DuckDuckGo automatically if Docker is unavailable.
- **`fossick install` registers the CLI.** Adds `fossick` to `safecmd_allowlist.json` in both the project and user `.claude/` dirs so the CLI runs without permission prompts.
- **`fetch(heavy=True)` and `automation_browser()` require Chrome.** Launches automatically if not running, but takes ~10s on first call.
- **`fetch(stealthy=True)` is slower** — use only when the site actively blocks the default fetcher.
- **`read_arxiv()` returns full paper markdown.** Papers are 30–100k chars. Always slice `paper['source']` before inserting into an LLM context: `paper['source'][:8000]`.
- **Always use `sel=` with `to_md()`.** `to_md(page)` includes nav, ads, and footers. Pick a CSS selector that targets the content: `.article-body`, `main`, `#content`, etc.
- **`CDPSession.sniff(url=None)` is passive** — it listens while the user browses. Pass `url=` to have fossick navigate automatically.
