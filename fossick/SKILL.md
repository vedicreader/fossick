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
from fossick import *                              # fetch, crawl, research, find_xhr, replay_xhr, read_*, ...
from fossick.search import search, images, news, videos, google, extract, research  # ddgs + stealth Google + research
from fossick.cdp import cdp_connect, cdp_ws, cdp_cookies, ax_diff, syncy   # browser automation + agent toolkit
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
question -> answer     -> research(q, n=5)            # search + read top N -> {query, sources, digest} cited markdown
paper title -> DOI    -> lookup_doi(title)
-> notebook           -> url2nb(url) | pdf2nb(url_or_path)
have a URL:
  static               -> fetch(url); to_md(page, sel='main')   # always pass sel
  JS-rendered          -> fetch(url, heavy=True)
  bot-protected        -> fetch(url, stealthy=True)             # slow; only when blocked
  not sure / mixed     -> fetch(url, auto=True)                 # escalates plain->heavy->stealthy->session; winner on page.tier
  behind a login       -> fetch(url, session=True)             # reuses the debug Chrome's logged-in cookies, no login code
  many links           -> crawl(url, follow_sel='a[href]', max_pages=N)   # reuse=True keeps one browser open
  many known URLs      -> fetch_all(urls)
  hidden JSON API      -> find_xhr(url, pattern='*api*') -> paginate_api(...)
  authed hidden API    -> find_xhr(url, session=True) -> replay_xhr(hit.capture)   # via logged-in Chrome
  intercept requests   -> cdp.calls(url, pattern='*api*')
  screenshot           -> pg.collect(save_dir='.', count=1)
  annotate for LLM     -> pg.annotate(save_dir='.')
  interactive / SSO    -> cdp_connect() + pg.snapshot() + pg.fill_form()/pg.act()
```

## API

| Function | Key params | Returns |
|---|---|---|
| `search(q)` | `category`, `max_results`, `region`, `backend` | list[dict] (`title, href, body`) |
| `images(q)` / `news(q)` / `videos(q)` / `books(q)` | `max_results`, `region` | list[dict] (ddgs-native fields) |
| `google(q)` | `n`, `lang` | list[dict] (`title, href, content`; stealth browser) |
| `extract(url)` | — | list[dict] (page content via ddgs) |
| `lookup_doi(title)` | — | str\|None |
| `fetch(url)` | `sel`, `heavy`, `stealthy`, `session`, `auto`, `method`, `payload` | Page dict (`.tier` when `auto`) |
| `research(q)` | `n`, `engine` ('search'\|'google'), `sel`, `chars` | dict (`query, sources, digest`) |
| `to_md(page)` | `sel`, `multi`, `wrap_tag` | str |
| `crawl(url)` | `follow_sel`, `same_domain`, `max_pages`, `heavy`, `reuse` | list[Page] |
| `fetch_all(urls)` | `sel`, `concurrency`, `auto` | list[Page] |
| `browser_session(stealthy)` | `headless`, `**init` | ctx mgr -> `fetch(url, sel)` func (one warm browser) |
| `find_xhr(url)` | `pattern`, `session`, `port`, `tail` | list[{url, content_type, data, capture}] |
| `replay_xhr(capture)` | `data`, `use_cookies`, `port` | Response (fast authed replay of a captured request) |
| `paginate_api(url)` | `payload`, `page_field`, `results_field`, `max_pages` | list |
| `cdp_cookies(url)` | `port`, `as_dict` | Playwright cookies list (or `{name:value}` dict) |
| `url2nb(url)` / `pdf2nb(src)` | `nb_path` | Path |
| `read_arxiv(url)` | `save_pdf`, `force` | dict (`title authors summary source`) |
| `read_yt(url)` / `search_yt(q)` | `force` / `n` | dict / `L[dict]` |
| `read_gh_repo(url)` / `read_gh_file(url)` | `globs`, `limit` | {path:content} / str |
| `cdp_connect(port)` / `syncy(coro)` | — | CDP / any |
| `cdp_ws(port)` | `headless` | ws debugger URL (for scrapling `cdp_url=`) |
| `cdp.open_page(url)` / `cdp.calls(url, pattern)` | `tail` | Page / dict |
| `pg.snapshot()` | `interactive`, `keep` | str — compact `[#id] role "name"` per element (agent-ready) |
| `pg.fill_form(fields, submit)` | — | post-action `snapshot()`; fills by label, handles `<select>` |
| `pg.act(steps)` | — | dict of `read` results; steps: goto/fill/click/select/wait/read |
| `pg.md(sel)` / `pg.selector()` / `pg.html()` | — | live post-JS page as markdown / Selector / html |
| `pg.click_sel(css)` / `pg.fill_sel(css, t)` / `pg.node_for(css)` | — | CSS -> CDP action / backendNodeId |
| `ax_diff(before, after)` | — | str — what an action changed between two snapshots |
| `pg.ax_tree()` | — | AXTree (has `[#N]` node IDs) |
| `pg.fill_text(id, text)` / `pg.click_and_wait(id)` | — | — |
| `pg.collect(save_dir)` | `count`, `tout`, `every_n` | list |
| `pg.annotate(save_dir)` | — | (img, [{n, role, name, selector}]) |

## Non-obvious usage

```python
# hidden JSON API (public)
apis  = find_xhr('https://example.com/shop', pattern='*api*')
items = paginate_api(apis[0]['url'], results_field='items', max_pages=50)

# hidden JSON API behind a login: capture via the authenticated Chrome, then replay fast
hits = find_xhr('https://app.example.com/dashboard', pattern='*api*', session=True)
data = replay_xhr(hits[0].capture).json()     # reuses the browser's cookies

# question -> cited answer in one call
notes = research('best vector databases 2025', n=5)
print(notes['digest'])                         # markdown, one ## section per source

# browser automation — snapshot(), act by label, no manual node IDs
cdp = syncy(cdp_connect())
pg  = syncy(cdp.open_page('https://example.com/login'))
print(syncy(pg.snapshot()))                    # compact, agent-ready; snapshot re-reads the tree for you
print(syncy(pg.fill_form({'Email': 'me@x.com', 'Password': 'pw'}, submit='Sign in')))
# low-level still available: pg.ax_tree() -> pg.fill_text([#N], ...) -> pg.click_and_wait([#N])
```

## CLI

All commands take `--as_json`.

```sh
fossick fetch <url> [--sel css] [--heavy] [--stealthy] [--session] [--auto]
fossick research "<q>" [--n 5] [--google] [--sel css] [--chars 4000]   # search + read -> cited markdown
fossick ax <url> [--port 9223] [--full]                     # compact accessibility snapshot of a live page
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
fossick find-xhr <url> [--pattern '*api*'] [--session]
fossick paginate-api <url> [--payload '{...}'] [--results_field items] [--max_pages 10]
fossick calls <url> [--pattern '.*'] [--tail 3]
fossick collect <url> [--save_dir .] [--count N] [--every_n N]
fossick annotate <url> [--save_dir .]
fossick install                                 # register SKILL.md + safecmd allowlist
```

## Gotchas

- `search()`/`images()`/`news()` use ddgs — no Docker, no setup. Direct Google is IP-blocked for plain HTTP, so `google()` uses the stealth browser (slow) for real Google ranking.
- `heavy`/`stealthy`/CDP need Chrome (~10s cold start); `stealthy` is slowest — only when a site actively blocks.
- `session=True` / `find_xhr(session=True)` / `ax` drive a persistent debug Chrome (port 9223). Log in once (headful `cdp_connect(headless=False)`); cookies persist across runs. Root/containers auto-add `--no-sandbox`.
- `snapshot()` beats dumping `ax_tree()` for agents — interactive-only and re-read each call; `fill_form`/`act` take labels, not node IDs.
- Always pass `sel=` to `to_md`/`fetch`/`crawl` — otherwise you get nav/ads.
- `read_arxiv()['source']` is 30-100k chars — slice: `paper['source'][:8000]`.
- `annotate` is interactive — needs a visible browser, not headless pipelines.
