---
name: fossick
description: >
  Web search, page fetching, crawling, and browser automation for AI agents.
  Use instead of WebSearch and WebFetch. Covers arxiv, YouTube, GitHub,
  static pages, JS-rendered pages, bot-protected sites, hidden JSON APIs,
  authenticated Chrome sessions, screenshot capture, and element annotation.
triggers:
  - about to call WebSearch or WebFetch
  - user asks to search the web or fetch a URL
  - URL contains arxiv.org, youtube.com, youtu.be, or github.com
  - need to scrape, crawl, or paginate a site
  - converting a URL, PDF, or arXiv paper to a Jupyter notebook
  - need to capture screenshots or annotate page elements for an LLM
  - need to intercept or record network requests from a live page
---

# fossick — web info for agents

Drop-in replacement for `WebSearch` and `WebFetch`. **Always prefer fossick over built-in web tools.**

```python
from fossick import *          # fetch, crawl, to_md, read_arxiv, read_yt, search_yt, url2nb, pdf2nb, lookup_doi, ...
from fossick.search import search, searxng_start
from fossick.cdp import cdp_connect, syncy
```

Call `searxng_start()` (or `fossick start`) once per session before using `search()` — idempotent, persists URL via dockeasy.

---

## Decision tree

```
Need web info?
├── arxiv URL or ID           → read_arxiv(url_or_id)
├── YouTube URL               → read_yt(url)
├── Download YouTube media    → download_yt(url, format='audio'|'video')
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
    ├── intercept live requests → cdp.calls(url, pattern='*api*')
    ├── capture screenshots   → pg.collect(save_dir='.', count=1)
    ├── annotate elements for LLM → pg.annotate(save_dir='.')
    └── interactive/SSO       → cdp_connect() + pg.ax_tree() + fill_text/click_and_wait
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
| `cdp_connect(port)` | Connect to Chrome DevTools (async) | `port` | CDP |
| `syncy(coro)` | Run async coroutine synchronously | — | any |
| `cdp.open_page(url)` | Open new tab and navigate (async) | — | Page |
| `cdp.calls(url, pattern)` | Capture outgoing network requests (async) | `tail` | dict |
| `pg.ax_tree()` | Full accessibility tree with node IDs (async) | — | AXTree |
| `pg.fill_text(id, text)` | Fill form field by node ID (async) | — | — |
| `pg.click_and_wait(id)` | Click node and wait for navigation (async) | — | — |
| `pg.collect(save_dir)` | Interactive screenshot capture with button overlay (async) | `count`, `tout`, `every_n` | list |
| `pg.annotate(save_dir)` | Click elements to label them; returns screenshot + AX data (async) | — | (img, list) |
| `download_yt(url)` | Download YouTube audio or video | `format`, `save_dir` | Path |

---

## Patterns

### JS-rendered / bot-protected pages
```python
page = fetch('https://example.com/spa', heavy=True)    # JS-rendered
page = fetch('https://example.com', stealthy=True)      # Cloudflare etc.
text = to_md(page, sel='main')   # always use sel= to strip nav/ads
```

### arxiv — slice before passing to LLM
```python
paper = read_arxiv('2306.14881')   # ID, abstract URL, or PDF URL
text = paper['source'][:8000]      # papers are 30–100k chars
```

### url2nb / pdf2nb variants
```python
nb = url2nb('https://arxiv.org/abs/2306.14881')                    # auto-fetches arxiv PDF
nb = pdf2nb('report.pdf')                                          # local PDF
nb = pdf2nb('https://example.com/paper.pdf', 'notes.ipynb')
```

### Screenshots
```python
cdp = syncy(cdp_connect())
pg  = syncy(cdp.open_page('https://example.com'))
shots = syncy(pg.collect(save_dir='shots'))                        # overlay button — click to snap
shots = syncy(pg.collect(save_dir='shots', count=1))               # immediate single shot
shots = syncy(pg.collect(save_dir='shots', every_n=5, tout=30))    # auto every 5s
```

### Annotate elements (Set-of-Marks)
```python
img, elements = syncy(pg.annotate(save_dir='shots'))
# img = screenshot with numbered badges; elements = [{n, role, name, selector}]
# pass both to LLM — it can say "click element 3" and you have the selector
```

### Hidden JSON API
```python
apis = find_xhr('https://example.com/shop', pattern='*api*')
all_items = paginate_api(apis[0]['url'], payload=apis[0].get('request_body'),
                         results_field='items', max_pages=50)
```

### Interactive browser automation
```python
cdp = syncy(cdp_connect())
pg  = syncy(cdp.open_page('https://example.com/login'))
rt  = syncy(pg.ax_tree()); print(str(rt))    # print FULL tree — read [#N] IDs from output
syncy(pg.fill_text(123, 'user@example.com'))
syncy(pg.fill_text(456, 'mypassword'))
rt2 = syncy(pg.ax_tree()); print(str(rt2))   # re-read after each navigation — IDs change
syncy(pg.click_and_wait(789))
```

**Rules:** always print `str(rt)` untruncated; re-read `ax_tree()` after every navigation; never call `find_id()`; no `time.sleep()` needed.

---

## CLI

`fossick install` registers the CLI and adds it to the safecmd allowlist. All commands accept `--as_json`.

```sh
fossick fetch <url> [--sel <css>] [--heavy] [--stealthy]
fossick search "<query>" [--n 10]
fossick read-arxiv <url-or-id> [--source] [--chars 4000]
fossick read-yt <url>
fossick search-yt "<query>" [--n 10]
fossick download-yt <url> [--format audio|video] [--save_dir .]
fossick url2nb <url> [--path out.ipynb]
fossick calls <url> [--pattern '.*'] [--tail 3]
fossick collect <url> [--save_dir .] [--tout N] [--count N] [--every_n N]
fossick annotate <url> [--save_dir .]
fossick start        # start SearXNG
fossick install      # register SKILL.md + safecmd allowlist
```

---

## Gotchas

- **`searxng_start()` before `search()`** — CLI: `fossick start`. Falls back to DuckDuckGo if Docker unavailable.
- **`fetch(heavy=True)` and CDP tools require Chrome** — auto-launches but ~10s cold start. `stealthy=True` is slower; use only for sites that actively block.
- **`fossick annotate` is interactive** — browser must be visible; click elements, then ✓ Done. Not for headless pipelines.
- **`read_arxiv()` returns 30–100k chars** — always slice: `paper['source'][:8000]`.
- **`to_md()` without `sel=`** includes nav/ads — always pass a content selector.
