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
  - URL is arxiv.org, youtube.com, youtu.be, or github.com
  - need to scrape, crawl, paginate, or hit a hidden JSON API
  - convert a URL, PDF, or arXiv paper to a notebook
  - screenshot, annotate, or intercept requests on a live page
---

# fossick

Drop-in for `WebSearch`/`WebFetch` — always prefer it.

```python
from fossick import *                              # fetch, crawl, read_*, url2nb, ...
from fossick.search import search, images, news, videos, google, extract  # ddgs metasearch + stealth Google
from fossick.cdp import cdp_connect, syncy         # browser automation
```

## Route

```
arxiv URL/ID          -> read_arxiv(id)              # dict; source is 30-100k chars, slice it
YouTube URL           -> read_yt(url)                # metadata + transcript
  download media       -> download_yt(url, format='audio'|'video')
  search               -> search_yt(q, n=10)
GitHub file / repo    -> read_gh_file(url) / read_gh_repo(url, globs=('README*','*.py'))
search query          -> search(q, max_results=10)   # ddgs metasearch, no Docker; dicts: title, href, body
  images/news/videos   -> images(q) | news(q) | videos(q)   # or search(q, category='images'|'news'|'videos')
  real Google ranking  -> google(q, n=10)             # stealth browser; slow, use when you need Google
  read a result URL    -> extract(url) | fetch(url)
paper title -> DOI    -> lookup_doi(title)
-> notebook           -> url2nb(url) | pdf2nb(url_or_path)
have a URL:
  static               -> fetch(url); to_md(page, sel='main')   # always pass sel
  JS-rendered          -> fetch(url, heavy=True)
  bot-protected        -> fetch(url, stealthy=True)             # slow; only when blocked
  many links           -> crawl(url, follow_sel='a[href]', max_pages=N)
  many known URLs      -> fetch_all(urls)
  hidden JSON API      -> find_xhr(url, pattern='*api*') -> paginate_api(...)
  intercept requests   -> cdp.calls(url, pattern='*api*')
  screenshot           -> pg.collect(save_dir='.', count=1)
  annotate for LLM     -> pg.annotate(save_dir='.')
  interactive / SSO    -> cdp_connect() + pg.ax_tree() + fill_text/click_and_wait
```

## API

| Function | Key params | Returns |
|---|---|---|
| `search(q)` | `category`, `max_results`, `region`, `backend` | list[dict] (`title, href, body`) |
| `images(q)` / `news(q)` / `videos(q)` / `books(q)` | `max_results`, `region` | list[dict] (ddgs-native fields) |
| `google(q)` | `n`, `lang` | list[dict] (`title, href, content`; stealth browser) |
| `extract(url)` | — | list[dict] (page content via ddgs) |
| `lookup_doi(title)` | — | str\|None |
| `fetch(url)` | `sel`, `heavy`, `stealthy`, `method`, `payload` | Page dict |
| `to_md(page)` | `sel`, `multi`, `wrap_tag` | str |
| `crawl(url)` | `follow_sel`, `same_domain`, `max_pages`, `heavy` | list[Page] |
| `fetch_all(urls)` | `sel`, `concurrency` | list[Page] |
| `find_xhr(url)` | `pattern` | list[{url, content_type, data}] |
| `paginate_api(url)` | `payload`, `page_field`, `results_field`, `max_pages` | list |
| `url2nb(url)` / `pdf2nb(src)` | `nb_path` | Path |
| `read_arxiv(url)` | `save_pdf`, `force` | dict (`title authors summary source`) |
| `read_yt(url)` / `search_yt(q)` | `force` / `n` | dict / `L[dict]` |
| `read_gh_repo(url)` / `read_gh_file(url)` | `globs`, `limit` | {path:content} / str |
| `cdp_connect(port)` / `syncy(coro)` | — | CDP / any |
| `cdp.open_page(url)` / `cdp.calls(url, pattern)` | `tail` | Page / dict |
| `pg.ax_tree()` | — | AXTree (has `[#N]` node IDs) |
| `pg.fill_text(id, text)` / `pg.click_and_wait(id)` | — | — |
| `pg.collect(save_dir)` | `count`, `tout`, `every_n` | list |
| `pg.annotate(save_dir)` | — | (img, [{n, role, name, selector}]) |

## Non-obvious usage

```python
# hidden JSON API
apis  = find_xhr('https://example.com/shop', pattern='*api*')
items = paginate_api(apis[0]['url'], results_field='items', max_pages=50)

# browser automation — print the tree, act on [#N] IDs, re-read after EVERY navigation
cdp = syncy(cdp_connect())
pg  = syncy(cdp.open_page('https://example.com/login'))
print(str(syncy(pg.ax_tree())))          # never truncate; IDs change per navigation
syncy(pg.fill_text(123, 'user@example.com'))
syncy(pg.click_and_wait(789))
# no time.sleep(); no find_id()
```

## CLI

All commands take `--as_json`.

```sh
fossick fetch <url> [--sel css] [--heavy] [--stealthy]
fossick crawl <url> [--follow_sel css] [--max_pages N] [--sel css]
fossick search "<q>" [--n 10] [--region us-en] [--google]   # --google: real Google via stealth browser
fossick images "<q>" [--n 20] [--region us-en]
fossick news "<q>" [--n 20] [--region us-en]
fossick videos "<q>" [--n 20] [--region us-en]
fossick lookup-doi "<title>"
fossick read-arxiv <url-or-id> [--source] [--chars 4000] [--force]
fossick read-yt <url> [--force]
fossick search-yt "<q>" [--n 10]
fossick download-yt <url> [--format audio|video] [--save_dir .]
fossick read-gh-file <blob-url>
fossick read-gh-repo <url> [--globs 'README*,*.py'] [--limit N]
fossick url2nb <url> [--path out.ipynb]
fossick pdf2nb <url-or-path> [--path out.ipynb] [--ocr auto|on|off]
fossick find-xhr <url> [--pattern '*api*']
fossick paginate-api <url> [--payload '{...}'] [--results_field items] [--max_pages 10]
fossick calls <url> [--pattern '.*'] [--tail 3]
fossick collect <url> [--save_dir .] [--count N] [--every_n N]
fossick annotate <url> [--save_dir .]
fossick install                                 # register SKILL.md + safecmd allowlist
```

## Gotchas

- `search()`/`images()`/`news()` use ddgs — no Docker, no setup. Direct Google is IP-blocked for plain HTTP, so `google()` uses the stealth browser (slow) for real Google ranking.
- `heavy`/`stealthy`/CDP need Chrome (~10s cold start); `stealthy` is slowest — only when a site actively blocks.
- Always pass `sel=` to `to_md`/`fetch`/`crawl` — otherwise you get nav/ads.
- `read_arxiv()['source']` is 30-100k chars — slice: `paper['source'][:8000]`.
- `annotate` is interactive — needs a visible browser, not headless pipelines.
